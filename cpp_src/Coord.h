#ifndef COORD_H
#define COORD_H

//0-255 max coord
class CoordLocal
{
public:
    typedef unsigned char Pos;
    CoordLocal(Pos x=0,Pos y=0);

    bool operator < (const CoordLocal& c) const;

    unsigned short int x() const;
    unsigned short int y() const;

private:
    unsigned short int pos_;
};

#include <iostream>
std::ostream& operator<<(std::ostream& ostr, const CoordLocal& cl);

// pair of coordinates for public use ( export/import )
struct Coord
{
    Coord(unsigned int x_, unsigned int y_)
        :x(x_)
        ,y(y_)
    {}

    Coord& operator+=(const CoordLocal& cl)
    {
      x+=cl.x();
      y+=cl.y();
      return *this;
    }

    unsigned int x,y;
};

#endif // COORD_H
