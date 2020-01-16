#include "PiSPI.hpp"

#define READ  0b1
#define WRITE 0b0
class Accel
{
public:
	Accel(uint8_t channel, int speed, int mode, uint8_t bitsperword);
	~Accel();


	bool read(uint8_t reg, uint8_t *buf, size_t length = 1);
	bool write(uint8_t reg, uint8_t val);

	virtual int32_t getX();
	virtual int32_t getY();
	virtual int32_t getZ();
	
private:
	PiSPI *m_piSPI = nullptr;
};
