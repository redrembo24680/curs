cmake_minimum_required(VERSION 3.10)
project(VotingSystemBackend)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Визначення джерел
set(SOURCES
    src/main.cpp
    src/controllers/ApiController.cpp
    src/http/HttpServer.cpp
    src/models/Player.cpp
    src/models/Team.cpp
    src/models/Match.cpp
    src/services/VotingService.cpp
    src/storage/SqliteStore.cpp
)

# Створення виконуваного файлу
add_executable(voting_server ${SOURCES})
target_include_directories(voting_server PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Налаштування для Windows
if(WIN32)
    target_link_libraries(voting_server ws2_32)
    
    # Try SQLite3 amalgamation first (single file, no external dependencies)
    set(SQLITE_AMALGAMATION_DIR "${CMAKE_SOURCE_DIR}/third_party/sqlite")
    if(EXISTS "${SQLITE_AMALGAMATION_DIR}/sqlite3.c")
        message(STATUS "Using SQLite3 amalgamation from third_party/sqlite")
        target_sources(voting_server PRIVATE "${SQLITE_AMALGAMATION_DIR}/sqlite3.c")
        target_include_directories(voting_server PRIVATE "${SQLITE_AMALGAMATION_DIR}")
        # Disable warnings for SQLite source (it's a third-party library)
        set_source_files_properties("${SQLITE_AMALGAMATION_DIR}/sqlite3.c" PROPERTIES COMPILE_FLAGS "/W0")
    else()
        # Try to find pre-installed SQLite3
        find_library(SQLITE3_LIB 
            NAMES sqlite3 sqlite3.lib
            PATHS 
                "C:/Program Files/SQLite/lib"
                "C:/sqlite/lib"
        )
        find_path(SQLITE3_INCLUDE_DIR
            NAMES sqlite3.h
            PATHS
                "C:/Program Files/SQLite/include"
                "C:/sqlite/include"
        )
        
        if(SQLITE3_LIB AND SQLITE3_INCLUDE_DIR)
            target_link_libraries(voting_server ${SQLITE3_LIB})
            target_include_directories(voting_server PRIVATE ${SQLITE3_INCLUDE_DIR})
            message(STATUS "Found SQLite3: ${SQLITE3_LIB}")
        else()
            message(WARNING "SQLite3 not found!")
            message(WARNING "Please either:")
            message(WARNING "  1. Download SQLite amalgamation and place sqlite3.c and sqlite3.h in third_party/sqlite/")
            message(WARNING "  2. Install SQLite3 and ensure it's in system paths")
            message(WARNING "  3. Use vcpkg: vcpkg install sqlite3:x64-windows")
        endif()
    endif()
else()
    target_link_libraries(voting_server stdc++fs)
    # On Linux, SQLite3 is usually in system libraries
    find_library(SQLITE3_LIB sqlite3)
    if(SQLITE3_LIB)
        target_link_libraries(voting_server ${SQLITE3_LIB})
        message(STATUS "Found SQLite3: ${SQLITE3_LIB}")
    else()
        # Try pkg-config
        find_package(PkgConfig)
        if(PkgConfig_FOUND)
            pkg_check_modules(SQLITE3 sqlite3)
            if(SQLITE3_FOUND)
                target_link_libraries(voting_server ${SQLITE3_LIBRARIES})
                target_include_directories(voting_server PRIVATE ${SQLITE3_INCLUDE_DIRS})
                message(STATUS "Found SQLite3 via pkg-config")
            else()
                message(WARNING "SQLite3 not found. Please install libsqlite3-dev")
            endif()
        endif()
    endif()
endif()

# Встановлення директорії виводу
set_target_properties(voting_server PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)


