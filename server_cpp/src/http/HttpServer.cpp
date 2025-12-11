#include "HttpServer.h"

#include <iostream>
#include <sstream>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

HttpServer::HttpServer(int port, ApiController& controller)
    : m_port(port), m_controller(controller) {
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
}

HttpServer::~HttpServer() {
#ifdef _WIN32
    WSACleanup();
#endif
}

void HttpServer::start() {
    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket < 0) {
        std::cerr << "Не вдалося створити сокет" << std::endl;
        return;
    }

    int opt = 1;
#ifdef _WIN32
    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<char*>(&opt), sizeof(opt));
#else
    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(m_port);

    if (bind(serverSocket, reinterpret_cast<sockaddr*>(&serverAddr), sizeof(serverAddr)) < 0) {
        std::cerr << "Не вдалося прив'язати порт " << m_port << std::endl;
        return;
    }

    if (listen(serverSocket, 16) < 0) {
        std::cerr << "Не вдалося розпочати прослуховування" << std::endl;
        return;
    }

    std::cout << "HTTP сервер запущено на порту " << m_port << std::endl;

    while (true) {
        sockaddr_in clientAddr{};
#ifdef _WIN32
        int clientLen = sizeof(clientAddr);
#else
        socklen_t clientLen = sizeof(clientAddr);
#endif
        int clientSocket = accept(serverSocket, reinterpret_cast<sockaddr*>(&clientAddr), &clientLen);
        if (clientSocket < 0) {
            std::cerr << "Помилка встановлення з'єднання" << std::endl;
            continue;
        }

        try {
            std::string request;
            char buffer[4096];
            int contentLength = 0;
            bool headersReceived = false;

            while (true) {
                const int bytesRead = recv(clientSocket, buffer, sizeof(buffer), 0);
                if (bytesRead <= 0) break;
                
                request.append(buffer, bytesRead);

                if (!headersReceived) {
                    auto headersEnd = request.find("\r\n\r\n");
                    if (headersEnd != std::string::npos) {
                        headersReceived = true;
                        
                        // Parse Content-Length
                        auto clPos = request.find("Content-Length: ");
                        if (clPos != std::string::npos) {
                            auto clEnd = request.find("\r\n", clPos);
                            contentLength = std::stoi(request.substr(clPos + 16, clEnd - (clPos + 16)));
                        }
                    }
                }

                // If we have headers and (no body or full body), stop reading
                if (headersReceived) {
                     auto bodyStartPos = request.find("\r\n\r\n") + 4;
                     if (request.size() >= bodyStartPos + contentLength) {
                         break;
                     }
                }
            }

            if (!request.empty()) {
                // Log basic request info
                auto firstLineEnd = request.find('\r');
                if (firstLineEnd != std::string::npos) {
                    std::cout << "Request: " << request.substr(0, firstLineEnd) << std::endl;
                }

                const auto response = handleRequest(request);
                
                // Send response
                const char* responseData = response.c_str();
                int totalSent = 0;
                int responseSize = static_cast<int>(response.size());
                
                while (totalSent < responseSize) {
                    int sent = send(clientSocket, responseData + totalSent, responseSize - totalSent, 0);
                    if (sent < 0) {
                        std::cerr << "Error sending response" << std::endl;
                        break;
                    }
                    totalSent += sent;
                }
            }
            
            // Graceful shutdown
#ifdef _WIN32
            shutdown(clientSocket, SD_SEND);
#else
            shutdown(clientSocket, SHUT_WR);
#endif
            
        } catch (const std::exception& ex) {
            std::cerr << "Error processing request: " << ex.what() << std::endl;
        } catch (...) {
            std::cerr << "Unknown error processing request" << std::endl;
        }

#ifdef _WIN32
        closesocket(clientSocket);
#else
        close(clientSocket);
#endif
    }
}

std::string HttpServer::handleRequest(const std::string& request) {
    try {
        const auto methodEnd = request.find(' ');
        if (methodEnd == std::string::npos) {
            return respond(R"({"error":"Invalid request"})");
        }

        const auto method = request.substr(0, methodEnd);
        const auto pathStart = methodEnd + 1;
        const auto pathEnd = request.find(' ', pathStart);
        if (pathEnd == std::string::npos) {
            return respond(R"({"error":"Invalid request"})");
        }

        const auto path = request.substr(pathStart, pathEnd - pathStart);

        if (method == "OPTIONS") {
            return respond("", "text/plain");
        }

    if (method == "GET") {
        if (path == "/" || path == "/api" || path == "/api/") {
            return respond(m_controller.handleRoot());
        }
        if (path == "/api/teams") {
            return respond(m_controller.handleTeamsGet());
        }
        if (path == "/api/players") {
            return respond(m_controller.handlePlayersGet());
        }
        if (path == "/api/matches") {
            return respond(m_controller.handleMatchesGet());
        }
        if (path == "/api/stats") {
            return respond(m_controller.handleStatsGet());
        }
        if (path == "/api/match-stats") {
            return respond(m_controller.handleMatchStatsGet());
        }
        if (path == "/api/dashboard" || path.rfind("/api/dashboard?", 0) == 0) {
            int matchId = 0;
            // Parse query parameter match_id if present
            auto queryStart = path.find("?match_id=");
            if (queryStart != std::string::npos) {
                try {
                    matchId = std::stoi(path.substr(queryStart + 10));
                } catch (...) {
                    matchId = 0;
                }
            }
            return respond(m_controller.handleDashboardGet(matchId));
        }
        if (path == "/api/matches-page") {
            return respond(m_controller.handleMatchesPageGet());
        }
        if (path == "/api/players-page") {
            return respond(m_controller.handlePlayersPageGet());
        }
        if (path == "/api/stats-page") {
            return respond(m_controller.handleStatsPageGet());
        }
        if (path.rfind("/api/votes/", 0) == 0) {
            int matchId = std::stoi(path.substr(std::string("/api/votes/").size()));
            return respond(m_controller.handleVotesGet(matchId));
        }
        if (path.rfind("/api/match-stats/", 0) == 0) {
            int matchId = std::stoi(path.substr(std::string("/api/match-stats/").size()));
            return respond(m_controller.handleGetMatchStats(matchId));
        }
    } else if (method == "POST") {
        auto body = parseJson(extractBody(request));
        if (path == "/api/teams/add") {
            return respond(m_controller.handleAddTeam(body));
        }
        if (path == "/api/players/add") {
            return respond(m_controller.handleAddPlayer(body));
        }
            if (path == "/api/matches/add") {
                return respond(m_controller.handleAddMatch(body));
            }
            if (path == "/api/vote") {
                return respond(m_controller.handleVote(body));
            }
            if (path == "/api/matches/close") {
                return respond(m_controller.handleCloseMatch(body));
            }
            if (path == "/api/matches/set-active") {
                return respond(m_controller.handleSetMatchActive(body));
            }
            if (path == "/api/matches/update-stats") {
                return respond(m_controller.handleUpdateMatchStats(body));
            }
        }

        return respond(R"({"error":"Route not found"})");
    } catch (const std::exception& ex) {
        std::cerr << "Handler error: " << ex.what() << std::endl;
        return respond(R"({"status":"error","message":"Internal Server Error"})");
    }
}

std::string HttpServer::extractBody(const std::string& request) {
    auto bodyStart = request.find("\r\n\r\n");
    if (bodyStart == std::string::npos) {
        return {};
    }
    return request.substr(bodyStart + 4);
}

std::map<std::string, std::string> HttpServer::parseJson(const std::string& body) {
    std::map<std::string, std::string> parsed;
    size_t pos = 0;
    while ((pos = body.find("\"", pos)) != std::string::npos) {
        auto keyStart = pos + 1;
        auto keyEnd = body.find("\"", keyStart);
        if (keyEnd == std::string::npos) break;
        auto key = body.substr(keyStart, keyEnd - keyStart);
        auto colonPos = body.find(":", keyEnd);
        if (colonPos == std::string::npos) break;
        auto valueStart = colonPos + 1;
        while (valueStart < body.size() && (body[valueStart] == ' ' || body[valueStart] == '\t')) ++valueStart;
        if (valueStart >= body.size()) break;

        std::string value;
        if (body[valueStart] == '"') {
            auto valueEnd = body.find("\"", valueStart + 1);
            if (valueEnd == std::string::npos) break;
            value = body.substr(valueStart + 1, valueEnd - valueStart - 1);
            pos = valueEnd + 1;
        } else {
            auto valueEnd = body.find_first_of(",}", valueStart);
            if (valueEnd == std::string::npos) valueEnd = body.size();
            value = body.substr(valueStart, valueEnd - valueStart);
            pos = valueEnd;
        }
        parsed[key] = value;
    }
    return parsed;
}

std::string HttpServer::respond(const std::string& body, const std::string& contentType) {
    std::ostringstream response;
    response << "HTTP/1.1 200 OK\r\n"
             << "Content-Type: " << contentType << "\r\n"
             << "Access-Control-Allow-Origin: *\r\n"
             << "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
             << "Access-Control-Allow-Headers: Content-Type\r\n"
             << "Connection: close\r\n"
             << "Content-Length: " << body.size() << "\r\n\r\n"
             << body;
    return response.str();
}






