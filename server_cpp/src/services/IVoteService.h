#pragma once
#include <string>

// Абстрактний інтерфейс для голосування
class IVoteService {
public:
    virtual ~IVoteService() = default;
    virtual bool recordVote(int matchId, int playerId, std::string& errorMessage) = 0;
};
