#include "Player.h"

Player::Player(int id, std::string name, std::string position, int teamId, int votes)
    : m_id(id), m_name(std::move(name)), m_position(std::move(position)), m_teamId(teamId), m_votes(votes) {}

std::ostream &operator<<(std::ostream &os, const Player &player)
{
    os << "Player[ID=" << player.m_id << ", Name=" << player.m_name << ", Position=" << player.m_position
       << ", TeamID=" << player.m_teamId << ", Votes=" << player.m_votes << "]";
    return os;
}

int Player::getId() const { return m_id; }

const std::string &Player::getName() const { return m_name; }

const std::string &Player::getPosition() const { return m_position; }

int Player::getTeamId() const { return m_teamId; }

int Player::getVotes() const { return m_votes; }

void Player::rename(const std::string &newName) { m_name = newName; }

void Player::updatePosition(const std::string &newPosition) { m_position = newPosition; }

void Player::setTeamId(int teamId) { m_teamId = teamId; }

void Player::incrementVote() { ++m_votes; }
