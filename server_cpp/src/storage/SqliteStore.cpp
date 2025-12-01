#include "SqliteStore.h"

#include <iostream>
#include <sstream>
#include <algorithm>
#include <cstring>
#include <stdexcept>
#include <filesystem>

#ifdef _WIN32
#include <windows.h>
#endif

SqliteStore::SqliteStore(const std::string& dbPath)
    : m_dbPath(dbPath), m_db(nullptr) {
    // Ensure the directory exists before opening database
    std::filesystem::path pathObj(dbPath);
    std::filesystem::path dir = pathObj.parent_path();
    if (!dir.empty() && !std::filesystem::exists(dir)) {
        try {
            std::filesystem::create_directories(dir);
            std::cout << "Created database directory: " << dir.string() << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "ERROR: Failed to create database directory: " << e.what() << std::endl;
            throw std::runtime_error("Failed to create database directory: " + std::string(e.what()));
        }
    }
    
    // On Windows, convert to wide string for proper Unicode handling
    // SQLite on Windows needs UTF-8 or wide string paths
    std::string pathToUse;
    
    #ifdef _WIN32
    // On Windows, convert path to wide string, then to UTF-8 for SQLite
    std::wstring wpath = pathObj.wstring();
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wpath.c_str(), (int)wpath.length(), NULL, 0, NULL, NULL);
    if (size_needed > 0) {
        pathToUse.resize(size_needed);
        WideCharToMultiByte(CP_UTF8, 0, wpath.c_str(), (int)wpath.length(), &pathToUse[0], size_needed, NULL, NULL);
    } else {
        // Fallback to regular string
        pathToUse = pathObj.string();
    }
    // Normalize separators for Windows
    std::replace(pathToUse.begin(), pathToUse.end(), '/', '\\');
    #else
    // On Linux/Mac, use regular string
    pathToUse = pathObj.string();
    #endif
    
    // Enable WAL mode for better concurrency and performance
    int rc = sqlite3_open(pathToUse.c_str(), &m_db);
    if (rc == SQLITE_OK) {
        // Enable WAL (Write-Ahead Logging) mode for better performance
        sqlite3_exec(m_db, "PRAGMA journal_mode=WAL;", nullptr, nullptr, nullptr);
        // Optimize for speed
        sqlite3_exec(m_db, "PRAGMA synchronous=NORMAL;", nullptr, nullptr, nullptr);
        sqlite3_exec(m_db, "PRAGMA cache_size=10000;", nullptr, nullptr, nullptr);
        sqlite3_exec(m_db, "PRAGMA temp_store=MEMORY;", nullptr, nullptr, nullptr);
    }
    if (rc != SQLITE_OK) {
        std::string errorMsg = m_db ? sqlite3_errmsg(m_db) : "unknown error";
        std::cerr << "ERROR: Can't open database: " << errorMsg << std::endl;
        std::cerr << "Database path: " << dbPath << std::endl;
        std::cerr << "Database path (normalized): " << pathToUse << std::endl;
        
        // Try to get absolute path for debugging (but don't use it for opening)
        try {
            std::filesystem::path absPath = std::filesystem::absolute(pathObj);
            std::cerr << "Database absolute path: " << absPath.string() << std::endl;
        } catch (...) {
            // Ignore if we can't get absolute path
        }
        
        if (m_db) {
            sqlite3_close(m_db);
        }
        m_db = nullptr;
        throw std::runtime_error("Failed to open SQLite database: " + errorMsg);
    }
    std::cout << "SQLite database opened successfully: " << pathToUse << std::endl;
    initializeDatabase();
}

SqliteStore::~SqliteStore() {
    if (m_db) {
        sqlite3_close(m_db);
    }
}

void SqliteStore::initializeDatabase() {
    if (!m_db) return;
    
    // Ensure the directory exists
    std::filesystem::path dbPath(m_dbPath);
    std::filesystem::path dbDir = dbPath.parent_path();
    if (!dbDir.empty() && !std::filesystem::exists(dbDir)) {
        try {
            std::filesystem::create_directories(dbDir);
            std::cout << "Created database directory: " << dbDir.string() << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "ERROR: Failed to create database directory: " << e.what() << std::endl;
        }
    }
    
    createTables();
    
    // Migrate existing matches to add formation columns if they don't exist
    // SQLite doesn't support IF NOT EXISTS for ALTER TABLE, so we check first
    sqlite3_stmt* checkStmt;
    const char* checkSql = "PRAGMA table_info(matches)";
    bool hasTeam1Formation = false;
    bool hasTeam2Formation = false;
    
    if (sqlite3_prepare_v2(m_db, checkSql, -1, &checkStmt, nullptr) == SQLITE_OK) {
        while (sqlite3_step(checkStmt) == SQLITE_ROW) {
            const unsigned char* colName = sqlite3_column_text(checkStmt, 1);
            if (colName) {
                std::string name = reinterpret_cast<const char*>(colName);
                if (name == "team1_formation") hasTeam1Formation = true;
                if (name == "team2_formation") hasTeam2Formation = true;
            }
        }
        sqlite3_finalize(checkStmt);
    }
    
    if (!hasTeam1Formation) {
        sqlite3_exec(m_db, "ALTER TABLE matches ADD COLUMN team1_formation TEXT DEFAULT '4-3-3'", nullptr, nullptr, nullptr);
    }
    if (!hasTeam2Formation) {
        sqlite3_exec(m_db, "ALTER TABLE matches ADD COLUMN team2_formation TEXT DEFAULT '4-3-3'", nullptr, nullptr, nullptr);
    }
}

void SqliteStore::createTables() {
    const char* sql = R"(
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            votes INTEGER DEFAULT 0,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            date TEXT NOT NULL,
            isActive INTEGER DEFAULT 1,
            team1_formation TEXT DEFAULT '4-3-3',
            team2_formation TEXT DEFAULT '4-3-3'
        );

        CREATE TABLE IF NOT EXISTS votes (
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            votes INTEGER DEFAULT 0,
            PRIMARY KEY (match_id, player_id),
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        );

        CREATE TABLE IF NOT EXISTS match_stats (
            match_id INTEGER PRIMARY KEY,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            date TEXT NOT NULL,
            isActive INTEGER DEFAULT 1,
            total_votes INTEGER DEFAULT 0,
            team1_votes INTEGER DEFAULT 0,
            team2_votes INTEGER DEFAULT 0,
            unique_voters INTEGER DEFAULT 0,
            most_voted_player_name TEXT,
            most_voted_player_votes INTEGER DEFAULT 0,
            team1_goals INTEGER DEFAULT 0,
            team2_goals INTEGER DEFAULT 0,
            team1_possession INTEGER DEFAULT 50,
            team2_possession INTEGER DEFAULT 50,
            team1_shots INTEGER DEFAULT 0,
            team2_shots INTEGER DEFAULT 0,
            team1_shots_on_target INTEGER DEFAULT 0,
            team2_shots_on_target INTEGER DEFAULT 0,
            team1_corners INTEGER DEFAULT 0,
            team2_corners INTEGER DEFAULT 0,
            team1_fouls INTEGER DEFAULT 0,
            team2_fouls INTEGER DEFAULT 0,
            team1_yellow_cards INTEGER DEFAULT 0,
            team2_yellow_cards INTEGER DEFAULT 0,
            team1_red_cards INTEGER DEFAULT 0,
            team2_red_cards INTEGER DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(id)
        );

        CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id);
        CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
        CREATE INDEX IF NOT EXISTS idx_votes_match ON votes(match_id);
        CREATE INDEX IF NOT EXISTS idx_votes_player ON votes(player_id);
        CREATE INDEX IF NOT EXISTS idx_matches_active ON matches(isActive);
        CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date);
        CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name);
    )";

    char* errMsg = nullptr;
    int rc = sqlite3_exec(m_db, sql, nullptr, nullptr, &errMsg);
    if (rc != SQLITE_OK) {
        std::cerr << "SQL error: " << errMsg << std::endl;
        sqlite3_free(errMsg);
    }
}

int SqliteStore::callbackInt(void* data, int argc, char** argv, char** azColName) {
    int* result = static_cast<int*>(data);
    if (argc > 0 && argv[0]) {
        *result = std::stoi(argv[0]);
    }
    return 0;
}

int SqliteStore::callbackString(void* data, int argc, char** argv, char** azColName) {
    std::string* result = static_cast<std::string*>(data);
    if (argc > 0 && argv[0]) {
        *result = argv[0];
    }
    return 0;
}

int SqliteStore::loadTeams(std::vector<Team>& teams) const {
    teams.clear();
    if (!m_db) {
        std::cerr << "ERROR: Database not open in loadTeams" << std::endl;
        return 1;
    }

    const char* sql = "SELECT id, name FROM teams ORDER BY id";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(m_db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "ERROR: Failed to prepare teams query: " << sqlite3_errmsg(m_db) << std::endl;
        return 1;
    }

    int maxId = 0;
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char* nameText = sqlite3_column_text(stmt, 1);
        const char* name = nameText ? reinterpret_cast<const char*>(nameText) : "";
        teams.emplace_back(id, name);
        if (id > maxId) maxId = id;
    }

    if (rc != SQLITE_DONE) {
        std::cerr << "ERROR: Failed to execute teams query: " << sqlite3_errmsg(m_db) << " (code: " << rc << ")" << std::endl;
        sqlite3_finalize(stmt);
        return 1;
    }

    sqlite3_finalize(stmt);
    std::cout << "Loaded " << teams.size() << " teams from database" << std::endl;
    return maxId > 0 ? maxId + 1 : 1;
}

int SqliteStore::loadPlayers(std::vector<Player>& players) const {
    players.clear();
    if (!m_db) {
        std::cerr << "ERROR: Database not open in loadPlayers" << std::endl;
        return 1;
    }

    // Optimized query with index on team_id
    const char* sql = "SELECT id, name, position, team_id, votes FROM players ORDER BY team_id, id";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(m_db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "ERROR: Failed to prepare players query: " << sqlite3_errmsg(m_db) << std::endl;
        return 1;
    }

    int maxId = 0;
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char* nameText = sqlite3_column_text(stmt, 1);
        const unsigned char* posText = sqlite3_column_text(stmt, 2);
        const char* name = nameText ? reinterpret_cast<const char*>(nameText) : "";
        const char* position = posText ? reinterpret_cast<const char*>(posText) : "";
        int teamId = sqlite3_column_int(stmt, 3);
        int votes = sqlite3_column_int(stmt, 4);
        
        players.emplace_back(id, name ? name : "", position ? position : "", teamId, votes);
        if (id > maxId) maxId = id;
    }

    if (rc != SQLITE_DONE) {
        std::cerr << "ERROR: Failed to execute players query: " << sqlite3_errmsg(m_db) << " (code: " << rc << ")" << std::endl;
        sqlite3_finalize(stmt);
        return 1;
    }

    sqlite3_finalize(stmt);
    std::cout << "Loaded " << players.size() << " players from database" << std::endl;
    return maxId > 0 ? maxId + 1 : 1;
}

int SqliteStore::loadMatches(std::vector<Match>& matches) const {
    matches.clear();
    if (!m_db) {
        std::cerr << "ERROR: Database not open in loadMatches" << std::endl;
        return 1;
    }

    // Optimized query - get active matches first, then by date
    const char* sql = "SELECT id, team1, team2, date, isActive, COALESCE(team1_formation, '4-3-3') as team1_formation, COALESCE(team2_formation, '4-3-3') as team2_formation FROM matches ORDER BY isActive DESC, date DESC, id";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(m_db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "ERROR: Failed to prepare matches query: " << sqlite3_errmsg(m_db) << std::endl;
        return 1;
    }

    int maxId = 0;
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char* team1Text = sqlite3_column_text(stmt, 1);
        const unsigned char* team2Text = sqlite3_column_text(stmt, 2);
        const unsigned char* dateText = sqlite3_column_text(stmt, 3);
        int isActive = sqlite3_column_int(stmt, 4);
        const unsigned char* team1FormationText = sqlite3_column_text(stmt, 5);
        const unsigned char* team2FormationText = sqlite3_column_text(stmt, 6);
        
        const char* team1 = team1Text ? reinterpret_cast<const char*>(team1Text) : "";
        const char* team2 = team2Text ? reinterpret_cast<const char*>(team2Text) : "";
        const char* date = dateText ? reinterpret_cast<const char*>(dateText) : "";
        const char* team1Formation = team1FormationText ? reinterpret_cast<const char*>(team1FormationText) : "4-3-3";
        const char* team2Formation = team2FormationText ? reinterpret_cast<const char*>(team2FormationText) : "4-3-3";
        
        matches.emplace_back(id, team1 ? team1 : "", team2 ? team2 : "", date ? date : "", isActive != 0, team1Formation ? team1Formation : "4-3-3", team2Formation ? team2Formation : "4-3-3");
        if (id > maxId) maxId = id;
    }

    if (rc != SQLITE_DONE) {
        std::cerr << "ERROR: Failed to execute matches query: " << sqlite3_errmsg(m_db) << " (code: " << rc << ")" << std::endl;
        sqlite3_finalize(stmt);
        return 1;
    }

    sqlite3_finalize(stmt);
    std::cout << "Loaded " << matches.size() << " matches from database" << std::endl;
    return maxId > 0 ? maxId + 1 : 1;
}

std::map<int, std::map<int, int>> SqliteStore::loadVotes() const {
    std::map<int, std::map<int, int>> result;
    if (!m_db) return result;

    // Optimized query with index on match_id
    const char* sql = "SELECT match_id, player_id, votes FROM votes ORDER BY match_id, player_id";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(m_db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        return result;
    }

    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int matchId = sqlite3_column_int(stmt, 0);
        int playerId = sqlite3_column_int(stmt, 1);
        int votes = sqlite3_column_int(stmt, 2);
        result[matchId][playerId] = votes;
    }

    if (rc != SQLITE_DONE) {
        std::cerr << "ERROR: Failed to execute votes query: " << sqlite3_errmsg(m_db) << " (code: " << rc << ")" << std::endl;
        sqlite3_finalize(stmt);
        return result;
    }

    sqlite3_finalize(stmt);
    std::cout << "Loaded " << result.size() << " match vote records from database" << std::endl;
    return result;
}

std::map<int, MatchStats> SqliteStore::loadMatchStats() const {
    std::map<int, MatchStats> result;
    if (!m_db) return result;

    const char* sql = R"(
        SELECT match_id, team1, team2, date, isActive,
               total_votes, team1_votes, team2_votes, unique_voters,
               most_voted_player_name, most_voted_player_votes,
               team1_goals, team2_goals,
               team1_possession, team2_possession,
               team1_shots, team2_shots,
               team1_shots_on_target, team2_shots_on_target,
               team1_corners, team2_corners,
               team1_fouls, team2_fouls,
               team1_yellow_cards, team2_yellow_cards,
               team1_red_cards, team2_red_cards
        FROM match_stats
        ORDER BY isActive DESC, date DESC
    )";
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(m_db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        return result;
    }

    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        MatchStats stats;
        stats.matchId = sqlite3_column_int(stmt, 0);
        const unsigned char* team1Text = sqlite3_column_text(stmt, 1);
        const unsigned char* team2Text = sqlite3_column_text(stmt, 2);
        const unsigned char* dateText = sqlite3_column_text(stmt, 3);
        stats.team1 = team1Text ? reinterpret_cast<const char*>(team1Text) : "";
        stats.team2 = team2Text ? reinterpret_cast<const char*>(team2Text) : "";
        stats.date = dateText ? reinterpret_cast<const char*>(dateText) : "";
        stats.isActive = sqlite3_column_int(stmt, 4) != 0;
        stats.totalVotes = sqlite3_column_int(stmt, 5);
        stats.team1Votes = sqlite3_column_int(stmt, 6);
        stats.team2Votes = sqlite3_column_int(stmt, 7);
        stats.uniqueVoters = sqlite3_column_int(stmt, 8);
        const unsigned char* mostVotedText = sqlite3_column_text(stmt, 9);
        stats.mostVotedPlayerName = mostVotedText ? reinterpret_cast<const char*>(mostVotedText) : "";
        stats.mostVotedPlayerVotes = sqlite3_column_int(stmt, 10);
        stats.team1Goals = sqlite3_column_int(stmt, 11);
        stats.team2Goals = sqlite3_column_int(stmt, 12);
        stats.team1Possession = sqlite3_column_int(stmt, 13);
        stats.team2Possession = sqlite3_column_int(stmt, 14);
        stats.team1Shots = sqlite3_column_int(stmt, 15);
        stats.team2Shots = sqlite3_column_int(stmt, 16);
        stats.team1ShotsOnTarget = sqlite3_column_int(stmt, 17);
        stats.team2ShotsOnTarget = sqlite3_column_int(stmt, 18);
        stats.team1Corners = sqlite3_column_int(stmt, 19);
        stats.team2Corners = sqlite3_column_int(stmt, 20);
        stats.team1Fouls = sqlite3_column_int(stmt, 21);
        stats.team2Fouls = sqlite3_column_int(stmt, 22);
        stats.team1YellowCards = sqlite3_column_int(stmt, 23);
        stats.team2YellowCards = sqlite3_column_int(stmt, 24);
        stats.team1RedCards = sqlite3_column_int(stmt, 25);
        stats.team2RedCards = sqlite3_column_int(stmt, 26);
        
        result[stats.matchId] = stats;
    }

    if (rc != SQLITE_DONE) {
        std::cerr << "ERROR: Failed to execute match_stats query: " << sqlite3_errmsg(m_db) << " (code: " << rc << ")" << std::endl;
        sqlite3_finalize(stmt);
        return result;
    }

    sqlite3_finalize(stmt);
    std::cout << "Loaded " << result.size() << " match stats records from database" << std::endl;
    return result;
}

void SqliteStore::saveAll(const std::vector<Player>& players,
                          const std::vector<Match>& matches,
                          const std::vector<Team>& teams,
                          const std::map<int, std::map<int, int>>& votes) const {
    if (!m_db) return;

    // Begin transaction
    sqlite3_exec(m_db, "BEGIN TRANSACTION", nullptr, nullptr, nullptr);

    // Save Teams
    sqlite3_exec(m_db, "DELETE FROM teams", nullptr, nullptr, nullptr);
    sqlite3_stmt* stmt = nullptr;
    const char* teamSql = "INSERT INTO teams (id, name) VALUES (?, ?)";
    int rc = sqlite3_prepare_v2(m_db, teamSql, -1, &stmt, nullptr);
    if (rc == SQLITE_OK) {
        for (const auto& team : teams) {
            sqlite3_bind_int(stmt, 1, team.getId());
            sqlite3_bind_text(stmt, 2, team.getName().c_str(), -1, SQLITE_STATIC);
            sqlite3_step(stmt);
            sqlite3_reset(stmt);
        }
        sqlite3_finalize(stmt);
    }

    // Save Players
    sqlite3_exec(m_db, "DELETE FROM players", nullptr, nullptr, nullptr);
    const char* playerSql = "INSERT INTO players (id, name, position, team_id, votes) VALUES (?, ?, ?, ?, ?)";
    rc = sqlite3_prepare_v2(m_db, playerSql, -1, &stmt, nullptr);
    if (rc == SQLITE_OK) {
        for (const auto& player : players) {
            sqlite3_bind_int(stmt, 1, player.getId());
            sqlite3_bind_text(stmt, 2, player.getName().c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_text(stmt, 3, player.getPosition().c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_int(stmt, 4, player.getTeamId());
            sqlite3_bind_int(stmt, 5, player.getVotes());
            sqlite3_step(stmt);
            sqlite3_reset(stmt);
        }
        sqlite3_finalize(stmt);
        stmt = nullptr;
    }

    // Save Matches
    sqlite3_exec(m_db, "DELETE FROM matches", nullptr, nullptr, nullptr);
    const char* matchSql = "INSERT OR REPLACE INTO matches (id, team1, team2, date, isActive, team1_formation, team2_formation) VALUES (?, ?, ?, ?, ?, ?, ?)";
    rc = sqlite3_prepare_v2(m_db, matchSql, -1, &stmt, nullptr);
    if (rc == SQLITE_OK) {
        for (const auto& match : matches) {
            sqlite3_bind_int(stmt, 1, match.getId());
            sqlite3_bind_text(stmt, 2, match.getTeam1().c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_text(stmt, 3, match.getTeam2().c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_text(stmt, 4, match.getDate().c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_int(stmt, 5, match.isActive() ? 1 : 0);
            sqlite3_bind_text(stmt, 6, match.getTeam1Formation().c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_text(stmt, 7, match.getTeam2Formation().c_str(), -1, SQLITE_STATIC);
            sqlite3_step(stmt);
            sqlite3_reset(stmt);
        }
        sqlite3_finalize(stmt);
        stmt = nullptr;
    }

    // Save Votes
    sqlite3_exec(m_db, "DELETE FROM votes", nullptr, nullptr, nullptr);
    const char* voteSql = "INSERT INTO votes (match_id, player_id, votes) VALUES (?, ?, ?)";
    rc = sqlite3_prepare_v2(m_db, voteSql, -1, &stmt, nullptr);
    if (rc == SQLITE_OK) {
        for (const auto& [matchId, playersVotes] : votes) {
            for (const auto& [playerId, count] : playersVotes) {
                sqlite3_bind_int(stmt, 1, matchId);
                sqlite3_bind_int(stmt, 2, playerId);
                sqlite3_bind_int(stmt, 3, count);
                sqlite3_step(stmt);
                sqlite3_reset(stmt);
            }
        }
        sqlite3_finalize(stmt);
        stmt = nullptr;
    }

    // Commit transaction
    sqlite3_exec(m_db, "COMMIT", nullptr, nullptr, nullptr);
}

void SqliteStore::saveMatchStats(const std::map<int, MatchStats>& matchStats) const {
    if (!m_db) return;

    sqlite3_exec(m_db, "BEGIN TRANSACTION", nullptr, nullptr, nullptr);
    sqlite3_exec(m_db, "DELETE FROM match_stats", nullptr, nullptr, nullptr);

    const char* sql = R"(
        INSERT INTO match_stats (
            match_id, team1, team2, date, isActive,
            total_votes, team1_votes, team2_votes, unique_voters,
            most_voted_player_name, most_voted_player_votes,
            team1_goals, team2_goals,
            team1_possession, team2_possession,
            team1_shots, team2_shots,
            team1_shots_on_target, team2_shots_on_target,
            team1_corners, team2_corners,
            team1_fouls, team2_fouls,
            team1_yellow_cards, team2_yellow_cards,
            team1_red_cards, team2_red_cards
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    )";

    sqlite3_stmt* stmt = nullptr;
    int rc = sqlite3_prepare_v2(m_db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        sqlite3_exec(m_db, "ROLLBACK", nullptr, nullptr, nullptr);
        return;
    }

    for (const auto& [matchId, stats] : matchStats) {
        int col = 0;
        sqlite3_bind_int(stmt, ++col, stats.matchId);
        sqlite3_bind_text(stmt, ++col, stats.team1.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, ++col, stats.team2.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, ++col, stats.date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, ++col, stats.isActive ? 1 : 0);
        sqlite3_bind_int(stmt, ++col, stats.totalVotes);
        sqlite3_bind_int(stmt, ++col, stats.team1Votes);
        sqlite3_bind_int(stmt, ++col, stats.team2Votes);
        sqlite3_bind_int(stmt, ++col, stats.uniqueVoters);
        sqlite3_bind_text(stmt, ++col, stats.mostVotedPlayerName.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, ++col, stats.mostVotedPlayerVotes);
        sqlite3_bind_int(stmt, ++col, stats.team1Goals);
        sqlite3_bind_int(stmt, ++col, stats.team2Goals);
        sqlite3_bind_int(stmt, ++col, stats.team1Possession);
        sqlite3_bind_int(stmt, ++col, stats.team2Possession);
        sqlite3_bind_int(stmt, ++col, stats.team1Shots);
        sqlite3_bind_int(stmt, ++col, stats.team2Shots);
        sqlite3_bind_int(stmt, ++col, stats.team1ShotsOnTarget);
        sqlite3_bind_int(stmt, ++col, stats.team2ShotsOnTarget);
        sqlite3_bind_int(stmt, ++col, stats.team1Corners);
        sqlite3_bind_int(stmt, ++col, stats.team2Corners);
        sqlite3_bind_int(stmt, ++col, stats.team1Fouls);
        sqlite3_bind_int(stmt, ++col, stats.team2Fouls);
        sqlite3_bind_int(stmt, ++col, stats.team1YellowCards);
        sqlite3_bind_int(stmt, ++col, stats.team2YellowCards);
        sqlite3_bind_int(stmt, ++col, stats.team1RedCards);
        sqlite3_bind_int(stmt, ++col, stats.team2RedCards);

        sqlite3_step(stmt);
        sqlite3_reset(stmt);
    }

    sqlite3_finalize(stmt);
    sqlite3_exec(m_db, "COMMIT", nullptr, nullptr, nullptr);
}


