#pragma once

#include <map>
#include <mutex>
#include <string>
#include <vector>

#include "models/Match.h"
#include "models/Player.h"
#include "models/Team.h"
#include "models/Stats.h"

#include "models/MatchStats.h"
#include "storage/SqliteStore.h"
#include "IVoteService.h"

class VotingService : public IVoteService {
public:
    explicit VotingService(const std::string& dataDirectory);

    Team addTeam(const std::string& name);
    Player addPlayer(const std::string& name, const std::string& position, int teamId);
    Match addMatch(const std::string& team1, const std::string& team2, const std::string& team1Formation = "4-3-3", const std::string& team2Formation = "4-3-3");
    bool recordVote(int matchId, int playerId, std::string& errorMessage) override;

    std::vector<Team> listTeams() const;
    std::vector<Player> listPlayers() const;
    std::vector<Match> listMatches() const;
    std::map<int, int> votesForMatch(int matchId) const;
    Stats collectStats() const;
    std::vector<MatchStats> collectMatchStats() const;
    bool closeMatch(int matchId, std::string& errorMessage);
    bool setMatchActive(int matchId, bool isActive, std::string& errorMessage);
    bool updateMatchStats(int matchId, const MatchStats& stats, std::string& errorMessage);
    MatchStats getMatchStats(int matchId) const;

private:
    SqliteStore m_store;
    mutable std::mutex m_mutex;
    std::vector<Team> m_teams;
    std::vector<Player> m_players;
    std::vector<Match> m_matches;
    std::map<int, std::map<int, int>> m_votes;
    std::map<int, MatchStats> m_matchStats; // matchId -> MatchStats
    int m_nextTeamId{1};
    int m_nextPlayerId{1};
    int m_nextMatchId{1};

    void persistUnlocked();
    static std::string makeTimestamp();
};






