#pragma once

#include <map>
#include <string>
#include <vector>
#include <sqlite3.h>

#include "models/Match.h"
#include "models/Player.h"
#include "models/Team.h"
#include "models/MatchStats.h"

class SqliteStore {
public:
    explicit SqliteStore(const std::string& dbPath);
    ~SqliteStore();

    // Disable copy constructor and assignment
    SqliteStore(const SqliteStore&) = delete;
    SqliteStore& operator=(const SqliteStore&) = delete;

    int loadTeams(std::vector<Team>& teams) const;
    int loadPlayers(std::vector<Player>& players) const;
    int loadMatches(std::vector<Match>& matches) const;
    std::map<int, std::map<int, int>> loadVotes() const;
    std::map<int, MatchStats> loadMatchStats() const;

    void saveAll(const std::vector<Player>& players,
                 const std::vector<Match>& matches,
                 const std::vector<Team>& teams,
                 const std::map<int, std::map<int, int>>& votes) const;
    void saveMatchStats(const std::map<int, MatchStats>& matchStats) const;

private:
    sqlite3* m_db;
    std::string m_dbPath;

    void initializeDatabase();
    void createTables();
    static int callbackInt(void* data, int argc, char** argv, char** azColName);
    static int callbackString(void* data, int argc, char** argv, char** azColName);
};


