#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <stdexcept>

static constexpr double PI = 3.14159265358979323846;

class Angle {
    double m_rad;
    double normalize(double angle_rad) const {
        angle_rad = fmod(angle_rad, 2 * PI);
        if (angle_rad < 0) {
            angle_rad += 2 * PI;
        }
        return angle_rad;
    }
public:
    Angle(): m_rad(0) {}
    Angle(double rad): m_rad(normalize(rad)) {}
    Angle(const Angle& other) : m_rad(other.m_rad) {}
    Angle& operator=(const Angle& other) {
        if (this != &other) {
            m_rad = other.m_rad;
        }
        return *this;
    }
    static Angle from_radians(double rad) {
        return Angle(rad);
    }
    static Angle from_degrees(double deg) {
        return Angle(deg * PI / 180.0);
    }
    double getRadians() const {
        return m_rad;
    }
    double getDegrees() const {
        return m_rad * 180.0 / PI;
    }
    Angle& setRadians(double rad) {
        m_rad = normalize(rad);
        return *this;
    }
    Angle& setDegrees(double deg) {
        m_rad = normalize(deg * PI / 180.0);
        return *this;
    }
    explicit operator float() const {
        return static_cast<float>(m_rad);
    }
    explicit operator int() const {
        return static_cast<int>(m_rad);
    }
    operator std::string() const {
        return std::to_string(m_rad) + " rad";
    }
    Angle operator+(const Angle& other) const {
        return Angle(m_rad + other.m_rad);
    } 
    Angle operator+(double rad) const {
        return Angle(m_rad + rad);
    }
    Angle operator-(const Angle& other) const {
        return Angle(m_rad - other.m_rad);
    }
    Angle operator-(double rad) const {
        return Angle(m_rad - rad);
    }
    Angle operator*(double factor) const {
        return Angle(m_rad * factor);
    }
    Angle operator/(double divisor) const {
        if (divisor == 0) { throw std::invalid_argument("Division by zero"); }
        return Angle(m_rad / divisor);
    }
    std::string str() const {
        return std::to_string(getDegrees()) + " deg";
    }
    std::string repr() const {
        return "Angle(" + std::to_string(m_rad) + " rad)";
    }
    bool operator==(const Angle& other) const {
        return std::fabs(m_rad - other.m_rad) < 1e-10;
    }
    bool operator!=(const Angle& other) const {
        return !(*this == other);
    }
    bool operator<(const Angle& other) const {
        return m_rad < other.m_rad;
    }
    bool operator>(const Angle& other) const {
        return m_rad > other.m_rad;
    }
    bool operator<=(const Angle& other) const {
        return m_rad <= other.m_rad;
    }
    bool operator>=(const Angle& other) const {
        return m_rad >= other.m_rad;
    }
    friend Angle operator+(double rad, const Angle& other) {
        return Angle(rad + other.m_rad);
    }
    friend Angle operator-(double rad, const Angle& other) {
        return Angle(rad - other.m_rad);
    }
    friend Angle operator*(double factor, const Angle& other) {
        return Angle(factor * other.m_rad);
    }
};

class AngleRange {
    Angle m_start;
    Angle m_end;
    bool m_in_start;
    bool m_in_end;
public:
    AngleRange(const Angle& start, const Angle& end, bool in_start = true, bool in_end = true):
        m_start(start), m_end(end), m_in_start(in_start), m_in_end(in_end) {}
    AngleRange(double start_rad, double end_rad, bool in_start = true, bool in_end = true):
        m_start(Angle::from_radians(start_rad)), m_end(Angle::from_radians(end_rad)), m_in_start(in_start), m_in_end(in_end) {}
    double length() const {
        double len = m_end.getRadians() - m_start.getRadians();
        if (len < 0) {
            len += 2 * PI;
        }
        return len;
    }
    bool operator==(const AngleRange& other) const {
        return m_start == other.m_start && m_end == other.m_end && m_in_start == other.m_in_start && m_in_end == other.m_in_end;
    } 
    bool operator!=(const AngleRange& other) const {
        return !(*this == other);
    }
    bool contains(const Angle& angle) const {
        bool left_ok = m_in_start ? (angle >= m_start) : (angle > m_start);
        bool right_ok = m_in_end ? (angle <= m_end) : (angle < m_end);
        return left_ok && right_ok;
    }
    bool contains(const AngleRange& other) const {
        return contains(other.m_start) && contains(other.m_end);
    }
    std::vector<AngleRange> operator+(const AngleRange& other) const {
        std::vector<AngleRange> result;
        if (this->contains(other.m_start) || this->contains(other.m_end) || other.contains(m_start) || other.contains(m_end)) {
            Angle start = (m_start < other.m_start) ? m_start : other.m_start;
            Angle end = (m_end > other.m_end) ? m_end : other.m_end;
            bool new_in_start = (m_start < other.m_start) ? m_in_start : other.m_in_start;
            bool new_in_end = (m_end > other.m_end) ? m_in_end : other.m_in_end;
            result.push_back(AngleRange(start, end, new_in_start, new_in_end));
        }
        else {
            result.push_back(*this);
            result.push_back(other);
        }
        return result;
    }
    std::vector<AngleRange> operator-(const AngleRange& other) const {
        std::vector<AngleRange> result;
        if (!this->contains(other.m_start) && !this->contains(other.m_end)) {
            result.push_back(*this);
            return result;
        }
        if (other.contains(*this)) {
            return result;
        }
        if (this->contains(other)) {
            if (m_start < other.m_start) {
                result.push_back(AngleRange(m_start, other.m_start, m_in_start, !other.m_in_start));
            }
            if (other.m_end < m_end) {
                result.push_back(AngleRange(other.m_end, m_end, !other.m_in_end, m_in_end));
            }
            return result;
        }
        if (this->contains(other.m_start)) {
            result.push_back(AngleRange(m_start, other.m_start, m_in_start, !other.m_in_start));
        }
        if (this->contains(other.m_end)) {
            result.push_back(AngleRange(other.m_end, m_end, !other.m_in_end, m_in_end));
        }
        return result;
    }   
    std::string str() const {
        return (m_in_start ? "[" : "(") + m_start.str() + "; " + m_end.str() + (m_in_end ? "]" : ")");
    }
    std::string repr() const {
        return "AngleRange(" + m_start.repr() + ", " + m_end.repr() + ", " + (m_in_start ? "true" : "false") + ", " + (m_in_end ? "true" : "false") + ")";
    }
};

int main() {
    Angle a1 = Angle::from_degrees(90);
    Angle a2 = Angle::from_radians(PI / 2);
    
    std::cout << "a1: " << a1.str() << std::endl;
    std::cout << "a2: " << a2.str() << std::endl;
    std::cout << "a1 == a2: " << (a1 == a2) << std::endl;
    
    AngleRange range1(Angle::from_degrees(0), Angle::from_degrees(90), true, false);
    AngleRange range2(Angle::from_degrees(60), Angle::from_degrees(180), true, true);
    
    std::cout << "range1: " << range1.str() << std::endl;
    std::cout << "range2: " << range2.str() << std::endl;
    std::cout << "range1 length: " << range1.length() << " rad" << std::endl;
    std::cout << "range2 length: " << range2.length() << " rad" << std::endl;
    
    std::cout << "a1 in range1: " << range1.contains(a1) << std::endl;
    std::cout << "a1 in range2: " << range2.contains(a1) << std::endl;

    std::vector<AngleRange> range1p2 = range1 + range2;
    std::vector<AngleRange> range1m2 = range1 - range2;
    
    std::cout << "range1 + range2: ";
    for (size_t i = 0; i < range1p2.size(); ++i) {
        std::cout << range1p2[i].str();
        if (i < range1p2.size() - 1) {
            std::cout << " + ";
        }
    }
    std::cout << std::endl;
    
    std::cout << "range1 - range2: ";
    for (size_t i = 0; i < range1m2.size(); ++i) {
        std::cout << range1m2[i].str();
        if (i < range1m2.size() - 1) {
            std::cout << " + ";
        }
    }
    std::cout << std::endl;
    
    return 0;
}
