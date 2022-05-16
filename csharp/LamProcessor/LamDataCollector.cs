using System;
using System.Linq;

namespace LamProcessor
{
    public class LamDataCollector
    {
        private static readonly int[] CARGO_CLASSES = { 2, 4, 5 };
        private static readonly int[] CAR_CLASSES = { 1, 3, 6 };

        public readonly ProcessedLamData result;

        public LamDataCollector(int lamId, int direction, int dayNumber)
        {
            result = new ProcessedLamData(lamId, dayNumber, direction);
            result.CargoSpeedMin = 999;
            result.CarSpeedMin = 999;
        }

        public void AddDataPoint(LamData data)
        {
            if (data.Faulty)
            {
                result.HadFaultyRows = true;
                return;
            }
            
            if (CAR_CLASSES.Contains(data.VecicleClass))
            {
                result.CarCount++;
                result.CarSpeed += data.SpeedKmPerHour;

                if (result.CarSpeedMax < data.SpeedKmPerHour)
                {
                    result.CarSpeedMax = data.SpeedKmPerHour;
                }
                if (result.CarSpeedMin > data.SpeedKmPerHour)
                {
                    result.CarSpeedMin = data.SpeedKmPerHour;
                }
            } 
            else if (CARGO_CLASSES.Contains(data.VecicleClass))
            {
                result.CargoCount++;
                result.CargoSpeed += data.SpeedKmPerHour;

                if (result.CargoSpeedMax < data.SpeedKmPerHour)
                {
                    result.CargoSpeedMax = data.SpeedKmPerHour;
                }
                if (result.CargoSpeedMin > data.SpeedKmPerHour)
                {
                    result.CargoSpeedMin = data.SpeedKmPerHour;
                }

                result.CargoLength += data.VehicleLenghtInMeters;
            }
        }

        public ProcessedLamData GetResult()
        {
            CalculateMeans();
            FixSpeeds();
            ScaleSpeeds();
            result.CargoLength = ScaleLength(result.CargoLength);
            result.CarCount = ScaleCarCount(result.CarCount);
            result.CargoCount = ScaleCargoCount(result.CargoCount);
            
            return result;
        }

        private int ScaleCarCount(int count)
        {
            var maxCount = 256 * 2; // Make assumption that no more than X vehicles pass a lam point in Y min interval.

            if (count > maxCount)
            {
                Console.WriteLine($"Car count {count} was more than the max count {maxCount}");
                count = maxCount;
            }

            return count * 256 / (maxCount + 1);
        }
        
        private int ScaleCargoCount(int count)
        {
            var maxCount = 60; // Make assumption that no more than X vehicles pass a lam point in Y min interval.

            if (count > maxCount)
            {
                count = maxCount;
            }

            return count * 256 / (maxCount + 1);
        }
        
        private void ScaleSpeeds()
        {
            result.CargoSpeedMean = ScaleSpeed(result.CargoSpeedMean);
            result.CargoSpeedMin = ScaleSpeed(result.CargoSpeedMin);
            result.CargoSpeedMax = ScaleSpeed(result.CargoSpeedMax);
            result.CarSpeedMean = ScaleSpeed(result.CarSpeedMean);
            result.CarSpeedMin = ScaleSpeed(result.CarSpeedMin);
            result.CarSpeedMax = ScaleSpeed(result.CarSpeedMax);
        }

        private int ScaleLength(double length)
        {
            var maxLength = 6000; // Maximum cumulative length of passing cargo vehicles.
            if (result.CargoLength >= maxLength)
            {
                Console.WriteLine($"Cargo length ({result.CargoLength}) was greater than max length {maxLength}");
                result.CargoLength = maxLength - 1;
            }

            return (int) (result.CargoLength / (maxLength + 1) * 256);
        }

        private void CalculateMeans()
        {
            result.CarSpeedMean = result.CarCount == 0 ? 0 : result.CarSpeed / result.CarCount;
            result.CargoSpeedMean = result.CargoCount == 0 ? 0 : result.CargoSpeed / result.CargoCount;
        }

        private int ScaleSpeed(int speed)
        {
            var maxSpeed = 200;
            var minSpeed = 20;

            if (speed < minSpeed)
            {
                speed = minSpeed;
            }
            else if (speed > maxSpeed)
            {
                // Console.WriteLine($"Speed ({speed}) was greater than max speed {maxSpeed}");
                speed = maxSpeed;
            }

            speed -= minSpeed;

            return speed * 256 / (maxSpeed - minSpeed + 1);
        }

        private void FixSpeeds()
        {
            if (result.CarCount == 0)
            {
                result.CarSpeedMin = 0;
            }
            if (result.CargoCount == 0)
            {
                result.CargoSpeedMin = 0;
            }
        }
    }
}