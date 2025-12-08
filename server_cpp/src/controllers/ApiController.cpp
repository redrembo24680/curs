#include "ApiController.h"

#include <algorithm>
#include <cctype>
#include <sstream>
#include "models/MatchStats.h"

ApiController::ApiController(VotingService& service) : m_service(service) {}

std::string ApiController::handleRoot() const {
    return R"({"message":"Voting System API","version":"2.0","status":"ok"})";
}

std::string ApiController::handleTeamsGet() const {
    auto teams = m_service.listTeams();
    std::ostringstream json;
    json << "{\"teams\":[";
    for (std::size_t i = 0; i < teams.size(); ++i) {
        const auto& t = teams[i];
        json << "{"
             << "\"id\":" << t.getId() << ","
             << "\"name\":\"" << escape(t.getName()) << "\""
             << "}";
        if (i + 1 < teams.size()) {
            json << ",";
        }
    }
    json << "]}";
    return json.str();
}

std::string ApiController::handlePlayersGet() const {
    auto players = m_service.listPlayers();
    std::ostringstream json;
    json << "{\"players\":[";
    for (std::size_t i = 0; i < players.size(); ++i) {
        const auto& p = players[i];
        json << "{"
             << "\"id\":" << p.getId() << ","
             << "\"name\":\"" << escape(p.getName()) << "\","
             << "\"position\":\"" << escape(p.getPosition()) << "\","
             << "\"team_id\":" << p.getTeamId() << ","
             << "\"votes\":" << p.getVotes()
             << "}";
        if (i + 1 < players.size()) {
            json << ",";
        }
    }
    json << "]}";
    return json.str();
}

std::string ApiController::handleMatchesGet() const {
    auto matches = m_service.listMatches();
    std::ostringstream json;
    json << "{\"matches\":[";
    for (std::size_t i = 0; i < matches.size(); ++i) {
        const auto& m = matches[i];
        json << "{"
             << "\"id\":" << m.getId() << ","
             << "\"team1\":\"" << escape(m.getTeam1()) << "\","
             << "\"team2\":\"" << escape(m.getTeam2()) << "\","
             << "\"date\":\"" << escape(m.getDate()) << "\","
             << "\"isActive\":" << (m.isActive() ? "true" : "false") << ","
             << "\"team1_formation\":\"" << escape(m.getTeam1Formation()) << "\","
             << "\"team2_formation\":\"" << escape(m.getTeam2Formation()) << "\""
             << "}";
        if (i + 1 < matches.size()) {
            json << ",";
        }
    }
    json << "]}";
    return json.str();
}

std::string ApiController::handleStatsGet() const {
    const auto stats = m_service.collectStats();
    std::ostringstream json;
    json << "{"
         << "\"total_players\":" << stats.totalPlayers << ","
         << "\"total_matches\":" << stats.totalMatches << ","
         << "\"total_votes\":" << stats.totalVotes
         << "}";
    return json.str();
}

std::string ApiController::handleMatchStatsGet() const {
    const auto matchStats = m_service.collectMatchStats();
    std::ostringstream json;
    json << "{\"matches\":[";
    for (std::size_t i = 0; i < matchStats.size(); ++i) {
        const auto& ms = matchStats[i];
        json << "{"
             << "\"match_id\":" << ms.matchId << ","
             << "\"team1\":\"" << escape(ms.team1) << "\","
             << "\"team2\":\"" << escape(ms.team2) << "\","
             << "\"date\":\"" << escape(ms.date) << "\","
             << "\"is_active\":" << (ms.isActive ? "true" : "false") << ","
             << "\"total_votes\":" << ms.totalVotes << ","
             << "\"team1_votes\":" << ms.team1Votes << ","
             << "\"team2_votes\":" << ms.team2Votes << ","
             << "\"unique_voters\":" << ms.uniqueVoters << ","
             << "\"most_voted_player\":\"" << escape(ms.mostVotedPlayerName) << "\","
             << "\"most_voted_player_votes\":" << ms.mostVotedPlayerVotes << ","
             << "\"team1_possession\":" << ms.team1Possession << ","
             << "\"team2_possession\":" << ms.team2Possession << ","
             << "\"team1_shots\":" << ms.team1Shots << ","
             << "\"team2_shots\":" << ms.team2Shots << ","
             << "\"team1_shots_on_target\":" << ms.team1ShotsOnTarget << ","
             << "\"team2_shots_on_target\":" << ms.team2ShotsOnTarget << ","
             << "\"team1_corners\":" << ms.team1Corners << ","
             << "\"team2_corners\":" << ms.team2Corners << ","
             << "\"team1_fouls\":" << ms.team1Fouls << ","
             << "\"team2_fouls\":" << ms.team2Fouls << ","
             << "\"team1_yellow_cards\":" << ms.team1YellowCards << ","
             << "\"team2_yellow_cards\":" << ms.team2YellowCards << ","
             << "\"team1_red_cards\":" << ms.team1RedCards << ","
             << "\"team2_red_cards\":" << ms.team2RedCards << ","
             << "\"team1_goals\":" << ms.team1Goals << ","
             << "\"team2_goals\":" << ms.team2Goals;
        json << "}";
        if (i + 1 < matchStats.size()) {
            json << ",";
        }
    }
    json << "]}";
    return json.str();
}

std::string ApiController::handleVotesGet(int matchId) const {
    auto votes = m_service.votesForMatch(matchId);
    std::ostringstream json;
    json << "{\"match_id\":" << matchId << ",\"votes\":[";
    bool first = true;
    for (const auto& [playerId, count] : votes) {
        if (!first) {
            json << ",";
        }
        json << "{"
             << "\"player_id\":" << playerId << ","
             << "\"votes\":" << count
             << "}";
        first = false;
    }
    json << "]}";
    return json.str();
}

std::string ApiController::handleAddTeam(const std::map<std::string, std::string>& body) const {
    const auto nameIt = body.find("name");
    if (nameIt == body.end() || nameIt->second.empty()) {
        return R"({"status":"error","message":"Необхідно вказати назву команди"})";
    }
    const auto team = m_service.addTeam(nameIt->second);
    std::ostringstream json;
    json << "{"
         << "\"status\":\"success\","
         << "\"team_id\":" << team.getId()
         << "}";
    return json.str();
}

std::string ApiController::handleAddPlayer(const std::map<std::string, std::string>& body) const {
    const auto nameIt = body.find("name");
    const auto positionIt = body.find("position");
    const auto teamIdIt = body.find("team_id");
    
    if (nameIt == body.end() || positionIt == body.end() || nameIt->second.empty()) {
        return R"({"status":"error","message":"Необхідно вказати ім'я та позицію гравця"})";
    }
    
    int teamId = 0;
    if (teamIdIt != body.end()) {
        try {
            teamId = std::stoi(teamIdIt->second);
        } catch (...) {}
    }

    const auto player = m_service.addPlayer(nameIt->second, positionIt->second, teamId);
    std::ostringstream json;
    json << "{"
         << "\"status\":\"success\","
         << "\"player_id\":" << player.getId()
         << "}";
    return json.str();
}

std::string ApiController::handleAddMatch(const std::map<std::string, std::string>& body) const {
    const auto first = body.find("team1");
    const auto second = body.find("team2");
    if (first == body.end() || second == body.end() || first->second.empty() || second->second.empty()) {
        return R"({"status":"error","message":"Необхідно вказати обидві команди"})";
    }
    
    const auto team1FormationIt = body.find("team1_formation");
    const auto team2FormationIt = body.find("team2_formation");
    const std::string team1Formation = (team1FormationIt != body.end() && !team1FormationIt->second.empty()) ? team1FormationIt->second : "4-3-3";
    const std::string team2Formation = (team2FormationIt != body.end() && !team2FormationIt->second.empty()) ? team2FormationIt->second : "4-3-3";
    
    const auto match = m_service.addMatch(first->second, second->second, team1Formation, team2Formation);
    std::ostringstream json;
    json << "{"
         << "\"status\":\"success\","
         << "\"match_id\":" << match.getId()
         << "}";
    return json.str();
}

std::string ApiController::handleVote(const std::map<std::string, std::string>& body) const {
    const auto matchIt = body.find("match_id");
    const auto playerIt = body.find("player_id");
    if (matchIt == body.end() || playerIt == body.end()) {
        return R"({"status":"error","message":"match_id та player_id є обов'язковими"})";
    }

    // ООП: створення користувача (fan)
    int userId = 1;
    Fan user(userId, "DemoFan");
    // std::cout << "User " << user.getName() << " (role: " << user.getRole() << ") проголосував за гравця " << playerIt->second << std::endl;

    int matchId = std::stoi(matchIt->second);
    int playerId = std::stoi(playerIt->second);
    std::string error;
    if (!m_service.recordVote(matchId, playerId, error)) {
        std::ostringstream json;
        json << "{"
             << "\"status\":\"error\","
             << "\"message\":\"" << escape(error) << "\""
             << "}";
        return json.str();
    }

    return R"({"status":"success","message":"Голос зараховано"})";
}

std::string ApiController::handleCloseMatch(const std::map<std::string, std::string>& body) const {
    const auto matchIt = body.find("match_id");
    if (matchIt == body.end()) {
        return R"({"status":"error","message":"match_id є обов'язковим"})";
    }

    int matchId = std::stoi(matchIt->second);
    std::string error;
    if (!m_service.closeMatch(matchId, error)) {
        std::ostringstream json;
        json << "{"
             << "\"status\":\"error\","
             << "\"message\":\"" << escape(error) << "\""
             << "}";
        return json.str();
    }

    return R"({"status":"success","message":"Матч завершено"})";
}

std::string ApiController::handleUpdateMatchStats(const std::map<std::string, std::string>& body) const {
    const auto matchIt = body.find("match_id");
    if (matchIt == body.end()) {
        return R"({"status":"error","message":"match_id є обов'язковим"})";
    }

    int matchId = std::stoi(matchIt->second);
    MatchStats stats = m_service.getMatchStats(matchId);
    
    // Update stats from body
    auto it = body.find("team1_possession");
    if (it != body.end()) stats.team1Possession = std::stoi(it->second);
    
    it = body.find("team2_possession");
    if (it != body.end()) stats.team2Possession = std::stoi(it->second);
    
    it = body.find("team1_shots");
    if (it != body.end()) stats.team1Shots = std::stoi(it->second);
    
    it = body.find("team2_shots");
    if (it != body.end()) stats.team2Shots = std::stoi(it->second);
    
    it = body.find("team1_shots_on_target");
    if (it != body.end()) stats.team1ShotsOnTarget = std::stoi(it->second);
    
    it = body.find("team2_shots_on_target");
    if (it != body.end()) stats.team2ShotsOnTarget = std::stoi(it->second);
    
    it = body.find("team1_corners");
    if (it != body.end()) stats.team1Corners = std::stoi(it->second);
    
    it = body.find("team2_corners");
    if (it != body.end()) stats.team2Corners = std::stoi(it->second);
    
    it = body.find("team1_fouls");
    if (it != body.end()) stats.team1Fouls = std::stoi(it->second);
    
    it = body.find("team2_fouls");
    if (it != body.end()) stats.team2Fouls = std::stoi(it->second);
    
    it = body.find("team1_yellow_cards");
    if (it != body.end()) stats.team1YellowCards = std::stoi(it->second);
    
    it = body.find("team2_yellow_cards");
    if (it != body.end()) stats.team2YellowCards = std::stoi(it->second);
    
    it = body.find("team1_red_cards");
    if (it != body.end()) stats.team1RedCards = std::stoi(it->second);
    
    it = body.find("team2_red_cards");
    if (it != body.end()) stats.team2RedCards = std::stoi(it->second);
    
    it = body.find("team1_goals");
    if (it != body.end()) stats.team1Goals = std::stoi(it->second);
    
    it = body.find("team2_goals");
    if (it != body.end()) stats.team2Goals = std::stoi(it->second);

    std::string error;
    if (!m_service.updateMatchStats(matchId, stats, error)) {
        std::ostringstream json;
        json << "{"
             << "\"status\":\"error\","
             << "\"message\":\"" << escape(error) << "\""
             << "}";
        return json.str();
    }

    return R"({"status":"success","message":"Статистику оновлено"})";
}

std::string ApiController::handleGetMatchStats(int matchId) const {
    MatchStats stats = m_service.getMatchStats(matchId);
    std::ostringstream json;
    json << "{"
         << "\"match_id\":" << stats.matchId << ","
         << "\"team1_possession\":" << stats.team1Possession << ","
         << "\"team2_possession\":" << stats.team2Possession << ","
         << "\"team1_shots\":" << stats.team1Shots << ","
         << "\"team2_shots\":" << stats.team2Shots << ","
         << "\"team1_shots_on_target\":" << stats.team1ShotsOnTarget << ","
         << "\"team2_shots_on_target\":" << stats.team2ShotsOnTarget << ","
         << "\"team1_corners\":" << stats.team1Corners << ","
         << "\"team2_corners\":" << stats.team2Corners << ","
         << "\"team1_fouls\":" << stats.team1Fouls << ","
         << "\"team2_fouls\":" << stats.team2Fouls << ","
         << "\"team1_yellow_cards\":" << stats.team1YellowCards << ","
         << "\"team2_yellow_cards\":" << stats.team2YellowCards << ","
         << "\"team1_red_cards\":" << stats.team1RedCards << ","
         << "\"team2_red_cards\":" << stats.team2RedCards << ","
         << "\"team1_goals\":" << stats.team1Goals << ","
         << "\"team2_goals\":" << stats.team2Goals
         << "}";
    return json.str();
}

std::string ApiController::handleDashboardGet(int matchId) const {
    // Get all data in one call
    auto teams = m_service.listTeams();
    auto players = m_service.listPlayers();
    auto matches = m_service.listMatches();
    const auto stats = m_service.collectStats();
    
    std::ostringstream json;
    json << "{";
    
    // Teams
    json << "\"teams\":[";
    for (std::size_t i = 0; i < teams.size(); ++i) {
        const auto& t = teams[i];
        json << "{\"id\":" << t.getId() << ",\"name\":\"" << escape(t.getName()) << "\"}";
        if (i + 1 < teams.size()) json << ",";
    }
    json << "],";
    
    // Players
    json << "\"players\":[";
    for (std::size_t i = 0; i < players.size(); ++i) {
        const auto& p = players[i];
        json << "{"
             << "\"id\":" << p.getId() << ","
             << "\"name\":\"" << escape(p.getName()) << "\","
             << "\"position\":\"" << escape(p.getPosition()) << "\","
             << "\"team_id\":" << p.getTeamId() << ","
             << "\"votes\":" << p.getVotes()
             << "}";
        if (i + 1 < players.size()) json << ",";
    }
    json << "],";
    
    // Matches
    json << "\"matches\":[";
    for (std::size_t i = 0; i < matches.size(); ++i) {
        const auto& m = matches[i];
        json << "{"
             << "\"id\":" << m.getId() << ","
             << "\"team1\":\"" << escape(m.getTeam1()) << "\","
             << "\"team2\":\"" << escape(m.getTeam2()) << "\","
             << "\"date\":\"" << escape(m.getDate()) << "\","
             << "\"isActive\":" << (m.isActive() ? "true" : "false") << ","
             << "\"team1_formation\":\"" << escape(m.getTeam1Formation()) << "\","
             << "\"team2_formation\":\"" << escape(m.getTeam2Formation()) << "\""
             << "}";
        if (i + 1 < matches.size()) json << ",";
    }
    json << "],";
    
    // Stats
    json << "\"stats\":{"
         << "\"total_players\":" << stats.totalPlayers << ","
         << "\"total_matches\":" << stats.totalMatches << ","
         << "\"total_votes\":" << stats.totalVotes
         << "}";
    
    // Votes for selected match (or first match if matchId is 0)
    int selectedMatchId = matchId;
    if (selectedMatchId == 0 && !matches.empty()) {
        selectedMatchId = matches[0].getId();
    }
    
    if (selectedMatchId > 0) {
        auto votes = m_service.votesForMatch(selectedMatchId);
        json << ",\"votes\":[";
        bool first = true;
        for (const auto& [playerId, count] : votes) {
            if (!first) json << ",";
            json << "{\"player_id\":" << playerId << ",\"votes\":" << count << "}";
            first = false;
        }
        json << "]";
    } else {
        json << ",\"votes\":[]";
    }
    
    json << "}";
    return json.str();
}

std::string ApiController::handleMatchesPageGet() const {
    // Combined endpoint for matches page: matches + teams
    auto matches = m_service.listMatches();
    auto teams = m_service.listTeams();
    
    std::ostringstream json;
    json << "{";
    
    // Matches
    json << "\"matches\":[";
    for (std::size_t i = 0; i < matches.size(); ++i) {
        const auto& m = matches[i];
        json << "{"
             << "\"id\":" << m.getId() << ","
             << "\"team1\":\"" << escape(m.getTeam1()) << "\","
             << "\"team2\":\"" << escape(m.getTeam2()) << "\","
             << "\"date\":\"" << escape(m.getDate()) << "\","
             << "\"isActive\":" << (m.isActive() ? "true" : "false") << ","
             << "\"team1_formation\":\"" << escape(m.getTeam1Formation()) << "\","
             << "\"team2_formation\":\"" << escape(m.getTeam2Formation()) << "\""
             << "}";
        if (i + 1 < matches.size()) json << ",";
    }
    json << "],";
    
    // Teams
    json << "\"teams\":[";
    for (std::size_t i = 0; i < teams.size(); ++i) {
        const auto& t = teams[i];
        json << "{\"id\":" << t.getId() << ",\"name\":\"" << escape(t.getName()) << "\"}";
        if (i + 1 < teams.size()) json << ",";
    }
    json << "]";
    
    json << "}";
    return json.str();
}

std::string ApiController::handlePlayersPageGet() const {
    // Combined endpoint for players page: players + teams
    auto players = m_service.listPlayers();
    auto teams = m_service.listTeams();
    
    std::ostringstream json;
    json << "{";
    
    // Players
    json << "\"players\":[";
    for (std::size_t i = 0; i < players.size(); ++i) {
        const auto& p = players[i];
        json << "{"
             << "\"id\":" << p.getId() << ","
             << "\"name\":\"" << escape(p.getName()) << "\","
             << "\"position\":\"" << escape(p.getPosition()) << "\","
             << "\"team_id\":" << p.getTeamId() << ","
             << "\"votes\":" << p.getVotes()
             << "}";
        if (i + 1 < players.size()) json << ",";
    }
    json << "],";
    
    // Teams
    json << "\"teams\":[";
    for (std::size_t i = 0; i < teams.size(); ++i) {
        const auto& t = teams[i];
        json << "{\"id\":" << t.getId() << ",\"name\":\"" << escape(t.getName()) << "\"}";
        if (i + 1 < teams.size()) json << ",";
    }
    json << "]";
    
    json << "}";
    return json.str();
}

std::string ApiController::handleStatsPageGet() const {
    // Combined endpoint for stats page: match-stats + top players
    const auto matchStats = m_service.collectMatchStats();
    auto players = m_service.listPlayers();
    
    // OPTIMIZATION: Create map for O(1) player lookup instead of O(n) find_if
    std::map<int, const Player*> playerMap;
    for (const auto& p : players) {
        playerMap[p.getId()] = &p;
    }
    
    // Sort players by votes and get top 10
    std::vector<std::pair<int, int>> playerVotes; // player_id, votes
    playerVotes.reserve(players.size()); // Pre-allocate for better performance
    for (const auto& p : players) {
        playerVotes.push_back({p.getId(), p.getVotes()});
    }
    std::sort(playerVotes.begin(), playerVotes.end(), 
              [](const auto& a, const auto& b) { return a.second > b.second; });
    
    std::ostringstream json;
    json << "{";
    
    // Match stats
    json << "\"matches\":[";
    for (std::size_t i = 0; i < matchStats.size(); ++i) {
        const auto& ms = matchStats[i];
        json << "{"
             << "\"match_id\":" << ms.matchId << ","
             << "\"team1\":\"" << escape(ms.team1) << "\","
             << "\"team2\":\"" << escape(ms.team2) << "\","
             << "\"date\":\"" << escape(ms.date) << "\","
             << "\"is_active\":" << (ms.isActive ? "true" : "false") << ","
             << "\"total_votes\":" << ms.totalVotes << ","
             << "\"team1_votes\":" << ms.team1Votes << ","
             << "\"team2_votes\":" << ms.team2Votes << ","
             << "\"unique_voters\":" << ms.uniqueVoters << ","
             << "\"most_voted_player\":\"" << escape(ms.mostVotedPlayerName) << "\","
             << "\"most_voted_player_votes\":" << ms.mostVotedPlayerVotes << ","
             << "\"team1_possession\":" << ms.team1Possession << ","
             << "\"team2_possession\":" << ms.team2Possession << ","
             << "\"team1_shots\":" << ms.team1Shots << ","
             << "\"team2_shots\":" << ms.team2Shots << ","
             << "\"team1_shots_on_target\":" << ms.team1ShotsOnTarget << ","
             << "\"team2_shots_on_target\":" << ms.team2ShotsOnTarget << ","
             << "\"team1_corners\":" << ms.team1Corners << ","
             << "\"team2_corners\":" << ms.team2Corners << ","
             << "\"team1_fouls\":" << ms.team1Fouls << ","
             << "\"team2_fouls\":" << ms.team2Fouls << ","
             << "\"team1_yellow_cards\":" << ms.team1YellowCards << ","
             << "\"team2_yellow_cards\":" << ms.team2YellowCards << ","
             << "\"team1_red_cards\":" << ms.team1RedCards << ","
             << "\"team2_red_cards\":" << ms.team2RedCards << ","
             << "\"team1_goals\":" << ms.team1Goals << ","
             << "\"team2_goals\":" << ms.team2Goals
             << "}";
        if (i + 1 < matchStats.size()) json << ",";
    }
    json << "],";
    
    // Top 10 players - OPTIMIZATION: Use map lookup instead of find_if
    json << "\"top_players\":[";
    std::size_t topCount = std::min(playerVotes.size(), static_cast<std::size_t>(10));
    for (std::size_t i = 0; i < topCount; ++i) {
        int playerId = playerVotes[i].first;
        int votes = playerVotes[i].second;
        
        // Use map for O(1) lookup instead of O(n) find_if
        auto playerIt = playerMap.find(playerId);
        if (playerIt != playerMap.end()) {
            const Player* p = playerIt->second;
            json << "{"
                 << "\"id\":" << p->getId() << ","
                 << "\"name\":\"" << escape(p->getName()) << "\","
                 << "\"position\":\"" << escape(p->getPosition()) << "\","
                 << "\"team_id\":" << p->getTeamId() << ","
                 << "\"votes\":" << votes
                 << "}";
            if (i + 1 < topCount) json << ",";
        }
    }
    json << "]";
    
    json << "}";
    return json.str();
}

std::string ApiController::escape(const std::string& value) {
    std::ostringstream oss;
    for (size_t i = 0; i < value.size(); ++i) {
        unsigned char ch = static_cast<unsigned char>(value[i]);
        switch (ch) {
            case '\"': oss << "\\\""; break;
            case '\\': 
                // Don't escape backslash if it's part of \uXXXX (already escaped sequence)
                // Check if we have \u followed by hex digits
                if (i + 5 < value.size() && value[i+1] == 'u' &&
                    isxdigit(value[i+2]) && isxdigit(value[i+3]) && 
                    isxdigit(value[i+4]) && isxdigit(value[i+5])) {
                    // This is already an escape sequence, don't double-escape
                    oss << ch;
                } else {
                    // Normal backslash, escape it
                    oss << "\\\\";
                }
                break;
            case '\n': oss << "\\n"; break;
            case '\r': oss << "\\r"; break;
            case '\t': oss << "\\t"; break;
            default: oss << ch;
        }
    }
    return oss.str();
}






