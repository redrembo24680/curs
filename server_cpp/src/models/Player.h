#pragma once

#include <string>
#include <ostream>

class Player {
public:
    Player() = default;
    Player(int id, std::string name, std::string position, int teamId = 0, int votes = 0);

    int getId() const;
    const std::string& getName() const;
    const std::string& getPosition() const;
    int getTeamId() const;
    int getVotes() const;

    void rename(const std::string& newName);
    void updatePosition(const std::string& newPosition);
    void setTeamId(int teamId);
    void incrementVote();

    friend std::ostream& operator<<(std::ostream& os, const Player& player);

private:
    int m_id{0};
    std::string m_name;
    std::string m_position;
    int m_teamId{0};
    int m_votes{0};
};






