#pragma once

#include <map>
#include <string>

#include "controllers/ApiController.h"

class HttpServer {
public:
    HttpServer(int port, ApiController& controller);
    ~HttpServer();

    void start();

private:
    int m_port;
    ApiController& m_controller;

    std::string handleRequest(const std::string& request);
    static std::string extractBody(const std::string& request);
    static std::map<std::string, std::string> parseJson(const std::string& body);
    static std::string respond(const std::string& body, const std::string& contentType = "application/json");
};










