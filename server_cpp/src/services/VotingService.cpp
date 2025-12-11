#include "VotingService.h"

#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <sstream>
#include "models/MatchStats.h"

VotingService::VotingService(const std::string &dataDirectory)
    : m_store(dataDirectory + std::string("/voting.db"))
{
    std::cout << "VotingService: Loading data from database..." << std::endl;
    m_nextTeamId = m_store.loadTeams(m_teams);
    std::cout << "VotingService: Loaded " << m_teams.size() << " teams, next ID: " << m_nextTeamId << std::endl;
    m_nextPlayerId = m_store.loadPlayers(m_players);
    std::cout << "VotingService: Loaded " << m_players.size() << " players, next ID: " << m_nextPlayerId << std::endl;
    m_nextMatchId = m_store.loadMatches(m_matches);
    std::cout << "VotingService: Loaded " << m_matches.size() << " matches, next ID: " << m_nextMatchId << std::endl;
    m_votes = m_store.loadVotes();
    std::cout << "VotingService: Loaded votes for " << m_votes.size() << " matches" << std::endl;
    m_matchStats = m_store.loadMatchStats();
    std::cout << "VotingService: Loaded stats for " << m_matchStats.size() << " matches" << std::endl;
    std::cout << "VotingService: Data loading complete" << std::endl;
}

Team VotingService::addTeam(const std::string &name)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    Team team(m_nextTeamId++, name);
    m_teams.push_back(team);
    persistUnlocked();
    return team;
}

Player VotingService::addPlayer(const std::string &name, const std::string &position, int teamId)
{
    std::lock_guard<std::mutex> lock(m_mutex);

    // Check for duplicate by name and team
    auto existing = std::find_if(m_players.begin(), m_players.end(),
                                 [&name, teamId](const Player &p)
                                 {
                                     return p.getName() == name && p.getTeamId() == teamId;
                                 });

    if (existing != m_players.end())
    {
        return *existing; // Return existing player instead of creating duplicate
    }

    Player player(m_nextPlayerId++, name, position, teamId, 0);
    m_players.push_back(player);
    persistUnlocked();
    return player;
}

Match VotingService::addMatch(const std::string &team1, const std::string &team2, const std::string &team1Formation, const std::string &team2Formation)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    Match match(m_nextMatchId++, team1, team2, makeTimestamp(), true, team1Formation, team2Formation);
    m_matches.push_back(match);

    // Initialize match stats with default values
    MatchStats stats;
    stats.matchId = match.getId();
    stats.team1 = team1;
    stats.team2 = team2;
    stats.date = match.getDate();
    stats.isActive = true;
    stats.team1Possession = 50;
    stats.team2Possession = 50;
    m_matchStats[match.getId()] = stats;

    persistUnlocked();
    return match;
}

bool VotingService::recordVote(int matchId, int playerId, std::string &errorMessage)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    auto matchIter = std::find_if(m_matches.begin(), m_matches.end(), [matchId](const Match &m)
                                  { return m.getId() == matchId && m.isActive(); });
    if (matchIter == m_matches.end())
    {
        errorMessage = "Матч не знайдено або вже завершено";
        return false;
    }

    auto playerIter = std::find_if(m_players.begin(), m_players.end(), [playerId](const Player &p)
                                   { return p.getId() == playerId; });
    if (playerIter == m_players.end())
    {
        errorMessage = "Гравця не знайдено";
        return false;
    }

    const_cast<Player &>(*playerIter).incrementVote();
    m_votes[matchId][playerId]++;
    persistUnlocked();
    return true;
}

std::vector<Team> VotingService::listTeams() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_teams;
}

std::vector<Player> VotingService::listPlayers() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_players;
}

std::vector<Match> VotingService::listMatches() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_matches;
}

std::map<int, int> VotingService::votesForMatch(int matchId) const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (m_votes.count(matchId) == 0)
    {
        return {};
    }
    return m_votes.at(matchId);
}

Stats VotingService::collectStats() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    Stats stats;
    stats.totalPlayers = m_players.size();
    stats.totalMatches = m_matches.size();
    int totalVotes = 0;
    for (const auto &[matchId, matchVotes] : m_votes)
    {
        (void)matchId;
        for (const auto &[playerId, count] : matchVotes)
        {
            (void)playerId;
            totalVotes += count;
        }
    }
    stats.totalVotes = totalVotes;
    return stats;
}

std::vector<MatchStats> VotingService::collectMatchStats() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    std::vector<MatchStats> result;

    // OPTIMIZATION: Create lookup maps ONCE instead of for each match
    // Map: playerId -> Player (for O(1) lookup)
    std::map<int, const Player *> playerMap;
    for (const auto &player : m_players)
    {
        playerMap[player.getId()] = &player;
    }

    // Map: teamName -> teamId (for O(1) lookup)
    std::map<std::string, int> teamNameToId;
    for (const auto &team : m_teams)
    {
        teamNameToId[team.getName()] = team.getId();
    }

    for (const auto &match : m_matches)
    {
        MatchStats stats;
        int matchId = match.getId();

        // Load saved stats if available
        if (m_matchStats.count(matchId) > 0)
        {
            stats = m_matchStats.at(matchId);
            // Always update team names and date from match (in case they're empty in stats)
            if (stats.team1.empty() || stats.team2.empty())
            {
                stats.team1 = match.getTeam1();
                stats.team2 = match.getTeam2();
            }
            if (stats.date.empty())
            {
                stats.date = match.getDate();
            }
            stats.isActive = match.isActive();
        }
        else
        {
            // Initialize with defaults
            stats.matchId = matchId;
            stats.team1 = match.getTeam1();
            stats.team2 = match.getTeam2();
            stats.date = match.getDate();
            stats.isActive = match.isActive();
            stats.team1Possession = 50;
            stats.team2Possession = 50;
        }

        // Get votes for this match
        if (m_votes.count(stats.matchId) > 0)
        {
            const auto &matchVotes = m_votes.at(stats.matchId);

            // Calculate totals and team votes
            int team1Votes = 0;
            int team2Votes = 0;
            int maxVotes = 0;
            int mostVotedPlayerId = 0;

            // Use pre-built maps for fast lookup
            int team1Id = teamNameToId.count(stats.team1) > 0 ? teamNameToId[stats.team1] : 0;
            int team2Id = teamNameToId.count(stats.team2) > 0 ? teamNameToId[stats.team2] : 0;

            for (const auto &[playerId, voteCount] : matchVotes)
            {
                stats.totalVotes += voteCount;
                stats.topPlayers[playerId] = voteCount;

                // OPTIMIZATION: Use map lookup instead of find_if (O(1) vs O(n))
                auto playerIt = playerMap.find(playerId);
                if (playerIt != playerMap.end())
                {
                    int playerTeamId = playerIt->second->getTeamId();
                    if (playerTeamId == team1Id)
                    {
                        team1Votes += voteCount;
                    }
                    else if (playerTeamId == team2Id)
                    {
                        team2Votes += voteCount;
                    }
                }

                if (voteCount > maxVotes)
                {
                    maxVotes = voteCount;
                    mostVotedPlayerId = playerId;
                }
            }

            stats.team1Votes = team1Votes;
            stats.team2Votes = team2Votes;
            stats.uniqueVoters = static_cast<int>(matchVotes.size());

            // OPTIMIZATION: Use map lookup instead of find_if
            if (mostVotedPlayerId > 0)
            {
                auto playerIt = playerMap.find(mostVotedPlayerId);
                if (playerIt != playerMap.end())
                {
                    stats.mostVotedPlayerName = playerIt->second->getName();
                    stats.mostVotedPlayerVotes = maxVotes;
                }
            }
        }

        result.push_back(stats);
    }

    // Sort by date (most recent first) or by total votes
    std::sort(result.begin(), result.end(), [](const MatchStats &a, const MatchStats &b)
              {
                  if (a.isActive != b.isActive)
                  {
                      return a.isActive; // Active matches first
                  }
                  return a.totalVotes > b.totalVotes; // Then by votes
              });

    return result;
}

void VotingService::persistUnlocked()
{
    m_store.saveAll(m_players, m_matches, m_teams, m_votes);
    m_store.saveMatchStats(m_matchStats);
}

bool VotingService::closeMatch(int matchId, std::string &errorMessage)
{
    return setMatchActive(matchId, false, errorMessage);
}

bool VotingService::setMatchActive(int matchId, bool isActive, std::string &errorMessage)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    auto matchIter = std::find_if(m_matches.begin(), m_matches.end(),
                                  [matchId](const Match &m)
                                  { return m.getId() == matchId; });

    if (matchIter == m_matches.end())
    {
        errorMessage = "Матч не знайдено";
        return false;
    }

    // Toggle or set the status
    if (isActive)
    {
        const_cast<Match &>(*matchIter).activate();
    }
    else
    {
        const_cast<Match &>(*matchIter).close();
    }

    persistUnlocked();
    return true;
}

bool VotingService::updateMatchStats(int matchId, const MatchStats &stats, std::string &errorMessage)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    auto matchIter = std::find_if(m_matches.begin(), m_matches.end(),
                                  [matchId](const Match &m)
                                  { return m.getId() == matchId; });

    if (matchIter == m_matches.end())
    {
        errorMessage = "Матч не знайдено";
        return false;
    }

    // Validate possession adds up to 100
    if (stats.team1Possession + stats.team2Possession != 100)
    {
        errorMessage = "Сума володіння м'ячем повинна дорівнювати 100%";
        return false;
    }

    m_matchStats[matchId] = stats;
    m_matchStats[matchId].matchId = matchId;
    m_matchStats[matchId].team1 = matchIter->getTeam1();
    m_matchStats[matchId].team2 = matchIter->getTeam2();
    m_matchStats[matchId].date = matchIter->getDate();
    m_matchStats[matchId].isActive = matchIter->isActive();

    persistUnlocked();
    return true;
}

bool VotingService::deleteMatch(int matchId, std::string &errorMessage)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    auto matchIter = std::find_if(m_matches.begin(), m_matches.end(),
                                  [matchId](const Match &m)
                                  { return m.getId() == matchId; });

    if (matchIter == m_matches.end())
    {
        errorMessage = "Матч не знайдено";
        return false;
    }

    // Remove match from vector
    m_matches.erase(matchIter);

    // Remove associated votes
    m_votes.erase(matchId);

    // Remove match stats
    m_matchStats.erase(matchId);

    persistUnlocked();
    return true;
}

MatchStats VotingService::getMatchStats(int matchId) const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (m_matchStats.count(matchId) > 0)
    {
        return m_matchStats.at(matchId);
    }

    // Return default stats if not found
    MatchStats stats;
    auto matchIter = std::find_if(m_matches.begin(), m_matches.end(),
                                  [matchId](const Match &m)
                                  { return m.getId() == matchId; });

    if (matchIter != m_matches.end())
    {
        stats.matchId = matchId;
        stats.team1 = matchIter->getTeam1();
        stats.team2 = matchIter->getTeam2();
        stats.date = matchIter->getDate();
        stats.isActive = matchIter->isActive();
        stats.team1Possession = 50;
        stats.team2Possession = 50;
    }

    return stats;
}

std::string VotingService::makeTimestamp()
{
    const auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tmStruct{};
#ifdef _WIN32
    localtime_s(&tmStruct, &t);
#else
    localtime_r(&t, &tmStruct);
#endif
    std::ostringstream oss;
    oss << std::put_time(&tmStruct, "%Y-%m-%d %H:%M:%S");
    return oss.str();
}
