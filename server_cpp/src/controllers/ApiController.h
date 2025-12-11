#pragma once

#include <map>
#include <string>

#include "services/VotingService.h"
#include "models/User.h"

class ApiController {
public:
    explicit ApiController(VotingService& service);

    std::string handleRoot() const;
    std::string handleTeamsGet() const;
    std::string handlePlayersGet() const;
    std::string handleMatchesGet() const;
    std::string handleStatsGet() const;
    std::string handleMatchStatsGet() const;
    std::string handleVotesGet(int matchId) const;
    std::string handleDashboardGet(int matchId = 0) const;
    std::string handleMatchesPageGet() const;
    std::string handlePlayersPageGet() const;
    std::string handleStatsPageGet() const;

    std::string handleAddTeam(const std::map<std::string, std::string>& body) const;
    std::string handleAddPlayer(const std::map<std::string, std::string>& body) const;
    std::string handleAddMatch(const std::map<std::string, std::string>& body) const;
    std::string handleVote(const std::map<std::string, std::string>& body) const;
    std::string handleCloseMatch(const std::map<std::string, std::string>& body) const;
    std::string handleSetMatchActive(const std::map<std::string, std::string>& body) const;
    std::string handleUpdateMatchStats(const std::map<std::string, std::string>& body) const;
    std::string handleDeleteMatch(const std::map<std::string, std::string>& body) const;
    std::string handleGetMatchStats(int matchId) const;

private:
    VotingService& m_service;

    static std::string escape(const std::string& value);
};






