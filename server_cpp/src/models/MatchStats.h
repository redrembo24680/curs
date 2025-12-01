#pragma once

#include <map>
#include <string>
#include <vector>

struct MatchStats {
    int matchId{0};
    std::string team1;
    std::string team2;
    std::string date;
    bool isActive{false};
    int totalVotes{0};
    int team1Votes{0};
    int team2Votes{0};
    int uniqueVoters{0};
    std::map<int, int> topPlayers; // playerId -> votes
    std::string mostVotedPlayerName;
    int mostVotedPlayerVotes{0};
    
    // Match statistics
    int team1Possession{50};      // Ball possession percentage
    int team2Possession{50};
    int team1Shots{0};             // Shots on goal
    int team2Shots{0};
    int team1ShotsOnTarget{0};     // Shots on target
    int team2ShotsOnTarget{0};
    int team1Corners{0};           // Corner kicks
    int team2Corners{0};
    int team1Fouls{0};             // Fouls
    int team2Fouls{0};
    int team1YellowCards{0};       // Yellow cards
    int team2YellowCards{0};
    int team1RedCards{0};          // Red cards
    int team2RedCards{0};
    int team1Goals{0};             // Goals scored
    int team2Goals{0};
};

