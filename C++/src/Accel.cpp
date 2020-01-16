#include "Accel.hpp"

Accel:Accel(uint8_t channel, int speed, int mode, uint8_t bitsperword)
{
	m_piSPI = new PiSPI(channel, speed, mode, bitsperword);
}

Accel:~Accel()
{
	if (m_piSPI != nullptr)
		delete m_piSPI;
}

bool Accel::read(uint8_t reg, uint8_t *buf, size_t length)
{
	if (piSPI == nullptr)
		return false;

	uint8_t address = (reg << 1) | 0b1;
	return piSPI->Read(address, buf, length);
}

bool Accel::write(uint8_t reg, uint8_t val)
{
	if (piSPI == nullptr)
		return false;

	uint8_t address = (reg << 1) & 0b11111110;
	return piSPI->Write(address, &val, 1);
}