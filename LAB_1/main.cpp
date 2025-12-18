#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <stdexcept>


class Angle {
    float m_rad;
    float normalize(float angle_rad) const {
        angle_rad = fmod(angle_rad, 2 * M_PI);
        if (angle_rad < 0) { angle_rad += 2 * M_PI; }
        return angle_rad;
    }
public:
    Angle(): m_rad(0) {}
    Angle(float rad): m_rad(rad) {}
    Angle(const Angle& other): m_rad(other.m_rad) {}
    Angle& operator=(const Angle& other) {
        if (this != &other) { m_rad = other.m_rad; }
        return *this;
    }
    static Angle from_radians(float rad) { return Angle(rad); }
    static Angle from_degrees(int deg) { return Angle(deg * M_PI / 180.0); }
    float getRadians() const { return m_rad; }
    int getDegrees() const { return std::round(m_rad * 180.0 / M_PI); }
    Angle& setRadians(float rad) {
        m_rad = rad;
        return *this;
    }
    Angle& setDegrees(float deg) {
        m_rad = deg * M_PI / 180.0;
        return *this;
    }
    explicit operator float() const { return static_cast<float>(m_rad); }
    explicit operator int() const { return static_cast<int>(m_rad); }
    operator std::string() const { return std::to_string(m_rad); }
    Angle operator+(const Angle& other) const { return Angle(m_rad + other.m_rad); } 
    Angle operator+(double rad) const { return Angle(m_rad + rad); }
    Angle operator-(const Angle& other) const { return Angle(m_rad - other.m_rad); }
    Angle operator-(float rad) const { return Angle(m_rad - rad); }
    Angle operator*(float factor) const { return Angle(m_rad * factor); }
    Angle operator/(float divisor) const {
        if (divisor == 0) { throw std::invalid_argument("Division by zero"); }
        return Angle(m_rad / divisor);
    }
    std::string str() const { return std::to_string(getDegrees()) + " deg"; }
    std::string repr() const { return "Angle(" + std::to_string(m_rad) + " rad)"; }
    bool operator==(const Angle& other) const {
        return std::fabs(normalize(m_rad) - normalize(other.m_rad)) < 1e-6f;
    }
    bool operator!=(const Angle& other) const {
        return !(*this == other);
    }
    bool operator<(const Angle& other) const {
        return normalize(m_rad) < normalize(other.m_rad);
    }
    bool operator>(const Angle& other) const {
        return normalize(m_rad) > normalize(other.m_rad);
    }
    bool operator<=(const Angle& other) const {
        return !(*this > other);
    }
    bool operator>=(const Angle& other) const {
        return !(*this < other);
    }
    friend Angle operator+(float rad, const Angle& other) { return Angle(rad + other.m_rad); }
    friend Angle operator-(float rad, const Angle& other) { return Angle(rad - other.m_rad); }
    friend Angle operator*(float factor, const Angle& other) { return Angle(factor * other.m_rad); }
};


class AngleRange {
    Angle m_start;
    Angle m_end;
    bool m_in_start;
    bool m_in_end;
public:
    AngleRange(const Angle& start,
        const Angle& end,
        bool in_start = true,
        bool in_end = true):
        m_start(start), m_end(end), m_in_start(in_start), m_in_end(in_end) {}
    AngleRange(float start_rad, float end_rad, bool in_start = true, bool in_end = true):
        m_start(Angle::from_radians(start_rad)), m_end(Angle::from_radians(end_rad)), 
        m_in_start(in_start), m_in_end(in_end) {}
    double length() const {
        float len = m_end.getRadians() - m_start.getRadians();
        if (len < 0) { len += 2 * M_PI; }
        return len;
    }
    bool operator==(const AngleRange& other) const {
        return m_start == other.m_start && m_end == other.m_end
            && m_in_start == other.m_in_start && m_in_end == other.m_in_end;
    } 
    bool operator!=(const AngleRange& other) const { return !(*this == other); }
    bool contains(const Angle& other) const {
        bool left_ok = m_in_start ? (other >= m_start) : (other > m_start);
        bool right_ok = m_in_end ? (other <= m_end) : (other < m_end);
        return left_ok && right_ok;
    }
    bool contains(const AngleRange& other) const {
        return contains(other.m_start) && contains(other.m_end);
    }
    std::vector<AngleRange> operator+(const AngleRange& other) const {
        std::vector<AngleRange> result;
        if (!(m_end < other.m_start || other.m_end < m_start)) {
            Angle new_start = (m_start < other.m_start) ? m_start : other.m_start;
            Angle new_end = (m_end > other.m_end) ? m_end : other.m_end;
            bool new_in_start = (m_start < other.m_start) ? m_in_start : other.m_in_start;
            bool new_in_end = (m_end > other.m_end) ? m_in_end : other.m_in_end;
            result.push_back(AngleRange(new_start, new_end, new_in_start, new_in_end));
        }
        else {
            result.push_back(*this);
            result.push_back(other);
        }
        return result;
    }
    std::vector<AngleRange> operator-(const AngleRange& other) const {
        std::vector<AngleRange> result;
        if (m_end < other.m_start || other.m_end < m_start) {
            result.push_back(*this);
            return result;
        }
        if (other.contains(*this)) { return result; }
        if (contains(other)) {
            if (m_start < other.m_start ||
                (m_start == other.m_start && m_in_start && !other.m_in_start)) {
                result.push_back(AngleRange(m_start, other.m_start, m_in_start, !other.m_in_start));
            }
            if (other.m_end < m_end ||
                (other.m_end == m_end && !other.m_in_end && m_in_end)) {
                result.push_back(AngleRange(other.m_end, m_end, !other.m_in_end, m_in_end));
            }
            return result;
        }
        if (contains(other.m_start)) {
            result.push_back(AngleRange(m_start, other.m_start, m_in_start, !other.m_in_start));
        }
        if (contains(other.m_end)) {
            result.push_back(AngleRange(other.m_end, m_end, !other.m_in_end, m_in_end));
        }
        return result;
    }
    std::string str() const {
        return (m_in_start ? "[" : "(") + m_start.str() + "; " + m_end.str() + (m_in_end ? "]" : ")");
    }
    std::string repr() const {
        return "AngleRange(" + m_start.repr() + ", " + m_end.repr() + ", " + 
               (m_in_start ? "true" : "false") + ", " + (m_in_end ? "true" : "false") + ")";
    }
};

int main() {
    Angle a1 = Angle::from_degrees(90);
    Angle a2 = Angle::from_radians(M_PI / 2);
    Angle a3 = Angle::from_degrees(45);
    Angle a4 = Angle::from_degrees(0);
    Angle a5 = Angle::from_degrees(360);
    
    std::cout << a1.str() << ": " << a1.repr() << std::endl;
    std::cout << a2.str() << ": " << a2.repr() << std::endl;
    std::cout << a3.str() << ": " << a3.repr() << std::endl;
    std::cout << a4.str() << ": " << a4.repr() << std::endl;
    std::cout << a5.str() << ": " << a5.repr() << std::endl;
    
    std::cout << a1.str() << " == " << a2.str() << ": " << (a1 == a2) << std::endl;
    std::cout << a1.str() << " > " << a3.str() << ": " << (a1 > a3) << std::endl;
    std::cout << a3.str() << " < " << a1.str() << ": " << (a3 < a1) << std::endl;
    std::cout << a4.str() << " == " << a5.str() << ": " << (a4 == a5) << std::endl;
    
    Angle sum = a1 + a3;
    Angle diff = a4 - a1;
    Angle mult = a1 * 2;
    Angle div = a4 / 2;
    
    std::cout << a1.str() << " + " << a3.str() << " = " << sum.str() << std::endl;
    std::cout << a4.str() << " - " << a1.str() << " = " << diff.str() << std::endl;
    std::cout << a1.str() << " * 2 = " << mult.str() << std::endl;
    std::cout << a4.str() << " / 2 = " << div.str() << std::endl;
    
    std::cout << a1.str() << " float: " << float(a1) << std::endl;
    std::cout << a1.str() << " int: " << int(a1) << std::endl;
    std::cout << a1.str() << " string: " << std::string(a1) << std::endl;
    std::cout << a1.str() << " repr: " << a1.repr() << std::endl;
    
    AngleRange range1(Angle::from_degrees(30), Angle::from_degrees(60), true, true);
    AngleRange range2(Angle::from_degrees(30), Angle::from_degrees(60), false, false);
    AngleRange range3(Angle::from_degrees(60), Angle::from_degrees(360), true, true);
    
    std::cout << range1.str() << " length: " << range1.length() << " rad" << std::endl;
    std::cout << range2.str() << " length: " << range2.length() << " rad" << std::endl;
    std::cout << range3.str() << " length: " << range3.length() << " rad" << std::endl;
    
    std::cout << a1.str() <<  " in " << range1.str() << ": " << range1.contains(a1) << std::endl;
    std::cout << a1.str() << " in " << range2.str() << ": " << range2.contains(a1) << std::endl;
    std::cout << a3.str() << " in " << range1.str() << ": " << range1.contains(a3) << std::endl;
    std::cout << a4.str() << " in " << range1.str() << ": " << range1.contains(a4) << std::endl;
    
    std::cout << range1.str() << " in " << range2.str() << ": " << range2.contains(range1) << std::endl;
    
    std::vector<AngleRange> r1p2 = range1 + range2;
    std::vector<AngleRange> r1m2 = range1 - range2;
    
    std::cout << range1.str() << " + "  << range2.str() << ": ";
    for (size_t i = 0; i < r1p2.size(); ++i) {
        std::cout << r1p2[i].str();
        if (i < r1p2.size() - 1) { std::cout << " U "; }
    }
    std::cout << std::endl;

    std::cout << range1.str() << " - "  << range2.str() << ": ";
    for (size_t i = 0; i < r1m2.size(); ++i) {
        std::cout << r1m2[i].str();
        if (i < r1m2.size() - 1) { std::cout << " U "; }
    }
    std::cout << std::endl;

    AngleRange range1_copy(range1);
    std::cout << range1.str() << " == " << range1_copy.str() << ": " << (range1 == range1_copy) << std::endl;
    std::cout << range1.str()  << " != " << range2.str() <<  ": " << (range1 != range2) << std::endl;
    
    return 0;
}

#endif