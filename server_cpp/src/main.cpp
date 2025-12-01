#include <filesystem>
#include <iostream>

#include "controllers/ApiController.h"
#include "http/HttpServer.h"
#include "services/VotingService.h"

int main(int argc, char* argv[]) {
    try {
        namespace fs = std::filesystem;
        fs::path exeDir = (argc > 0) ? fs::path(argv[0]).parent_path() : fs::current_path();
        
        // Determine data directory path
        // Try to find server_cpp/data relative to executable location
        fs::path dataDir;
        
        // If running from build/bin/Release/voting_server.exe
        // Go up: build/bin/Release -> build/bin -> build -> server_cpp -> data
        fs::path try1 = fs::weakly_canonical(exeDir / ".." / ".." / ".." / "data");
        // If running from build/Release/voting_server.exe  
        // Go up: build/Release -> build -> server_cpp -> data
        fs::path try2 = fs::weakly_canonical(exeDir / ".." / ".." / "data");
        
        // Check if server_cpp directory exists in parent paths
        if (fs::exists(try1.parent_path() / "src") || fs::exists(try1.parent_path() / "CMakeLists.txt")) {
            dataDir = try1;
        } else if (fs::exists(try2.parent_path() / "src") || fs::exists(try2.parent_path() / "CMakeLists.txt")) {
            dataDir = try2;
        } else {
            // Fallback: use server_cpp/data from project root
            // Go up from exe: build/bin/Release -> build/bin -> build -> .. -> server_cpp/data
            fs::path projectRoot = fs::weakly_canonical(exeDir / ".." / ".." / ".." / ".." / "server_cpp" / "data");
            if (fs::exists(projectRoot.parent_path())) {
                dataDir = projectRoot;
            } else {
                // Last resort: use build/data
                dataDir = fs::weakly_canonical(exeDir / ".." / "data");
            }
        }
        
        // Ensure data directory exists
        if (!fs::exists(dataDir)) {
            std::cout << "Creating data directory: " << dataDir.string() << std::endl;
            fs::create_directories(dataDir);
        }
        
        fs::path dbPath = dataDir / "voting.db";
        std::cout << "Database path: " << dbPath.string() << std::endl;
        
        // Use native string() - SqliteStore will handle UTF-8 conversion internally
        std::string dataDirStr = dataDir.string();
        
        VotingService service(dataDirStr);
        ApiController controller(service);
        HttpServer server(8080, controller);
        server.start();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal server error: " << ex.what() << std::endl;
        return 1;
    }
    return 0;
}

