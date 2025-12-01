#pragma once

#include <string>

class Match {
public:
    Match() = default;
    Match(int id, std::string firstTeam, std::string secondTeam, std::string date, bool active = true, std::string team1Formation = "4-3-3", std::string team2Formation = "4-3-3");

    int getId() const;
    const std::string& getTeam1() const;
    const std::string& getTeam2() const;
    const std::string& getDate() const;
    bool isActive() const;
    const std::string& getTeam1Formation() const;
    const std::string& getTeam2Formation() const;

    void close();

private:
    int m_id{0};
    std::string m_team1;
    std::string m_team2;
    std::string m_date;
    bool m_isActive{true};
    std::string m_team1Formation{"4-3-3"};
    std::string m_team2Formation{"4-3-3"};
};










