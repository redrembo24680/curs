# Makefile для збірки C++ backend

CXX = g++
CXXFLAGS = -std=c++17 -Wall -O2 -Isrc
TARGET = voting_server
SRCS = \
	src/main.cpp \
	src/controllers/ApiController.cpp \
	src/http/HttpServer.cpp \
	src/models/Player.cpp \
	src/models/Team.cpp \
	src/models/Match.cpp \
	src/services/VotingService.cpp \
	src/storage/JsonFileStore.cpp

# Для Windows
ifeq ($(OS),Windows_NT)
	LDFLAGS = -lws2_32
	TARGET = voting_server.exe
	MKDIR = mkdir
	RM = del /Q
else
	LDFLAGS = -pthread -lstdc++fs
	MKDIR = mkdir -p
	RM = rm -rf
endif

all: $(TARGET)

$(TARGET): $(SRCS)
	$(MKDIR) bin
	$(CXX) $(CXXFLAGS) -o bin/$(TARGET) $(SRCS) $(LDFLAGS)
	@echo "Backend сервер скомпільовано: bin/$(TARGET)"

clean:
	$(RM) bin/$(TARGET) bin/*.exe
	@echo "Очищено збірку"

run: $(TARGET)
	@echo "Запуск backend сервера..."
	bin/$(TARGET)

.PHONY: all clean run


