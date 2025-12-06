#include "Team.h"

Team::Team(int id, std::string name)
    : m_id(id), m_name(std::move(name)) {}

int Team::getId() const { return m_id; }

const std::string& Team::getName() const { return m_name; }












