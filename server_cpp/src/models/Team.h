#pragma once

#include <string>

class Team {
public:
    Team() = default;
    Team(int id, std::string name);

    int getId() const;
    const std::string& getName() const;

private:
    int m_id{0};
    std::string m_name;
};





