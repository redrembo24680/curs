#include "Match.h"

Match::Match(int id, std::string firstTeam, std::string secondTeam, std::string date, bool active, std::string team1Formation, std::string team2Formation)
    : m_id(id),
      m_team1(std::move(firstTeam)),
      m_team2(std::move(secondTeam)),
      m_date(std::move(date)),
      m_isActive(active),
      m_team1Formation(std::move(team1Formation)),
      m_team2Formation(std::move(team2Formation)) {}

int Match::getId() const { return m_id; }

const std::string &Match::getTeam1() const { return m_team1; }

const std::string &Match::getTeam2() const { return m_team2; }

const std::string &Match::getDate() const { return m_date; }

bool Match::isActive() const { return m_isActive; }

const std::string &Match::getTeam1Formation() const { return m_team1Formation; }

const std::string &Match::getTeam2Formation() const { return m_team2Formation; }

void Match::close() { m_isActive = false; }

void Match::activate() { m_isActive = true; }
