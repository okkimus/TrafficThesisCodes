using CsvHelper.Configuration.Attributes;

namespace LamProcessor
{
    public class LamData
    {
        [Index(0)]
        public int LamId { get; set; }

        [Index(1)]
        public int Year { get; set; }
        
        [Index(2)]
        public int NumberOfDay { get; set; }

        [Index(3)]
        public int Hour { get; set; }
        
        [Index(4)]
        public int Minute { get; set; }
        
        [Index(7)]
        public double VehicleLenghtInMeters { get; set; }
        
        [Index(9)]
        public int Direction { get; set; }
        
        [Index(10)]
        public int VecicleClass { get; set; }

        [Index(11)]
        public int SpeedKmPerHour { get; set; }
        
        [Index(12)]
        public bool Faulty { get; set; }
    }
}