#pragma once
#include <string>

// Абстрактний клас (інтерфейс)
class User {
public:
    User(int id, const std::string& name) : m_id(id), m_name(name) {}
    virtual ~User() = default;
    int getId() const { return m_id; }
    const std::string& getName() const { return m_name; }
    virtual std::string getRole() const = 0; // Поліморфізм
protected:
    int m_id;
    std::string m_name;
};

class Fan : public User {
public:
    Fan(int id, const std::string& name) : User(id, name) {}
    std::string getRole() const override { return "fan"; }
};

class Admin : public User {
public:
    Admin(int id, const std::string& name) : User(id, name) {}
    std::string getRole() const override { return "admin"; }
};
