namespace LamProcessor
{
    public class ProcessedLamData
    {
        public int CargoSpeed { get; set; } = 0;
        public int CarSpeed { get; set; } = 0;
        public int CargoSpeedMin { get; set; } = 0;
        public int CarSpeedMin { get; set; } = 0;
        public int CargoSpeedMax { get; set; } = 0;
        public int CarSpeedMax { get; set; } = 0;
        public int CargoSpeedMean { get; set; } = 0;
        public int CarSpeedMean { get; set; } = 0;

        public int CargoCount { get; set; } = 0;
        public int CarCount { get; set; } = 0;
        public double CargoLength { get; set; } = 0;
        public bool HadFaultyRows { get; set; } = false;


        public readonly int LamId;
        public readonly int DayNumber;
        public readonly int Direction;

        public ProcessedLamData(int lamId, int dayNumber, int direction)
        {
            LamId = lamId;
            DayNumber = dayNumber;
            Direction = direction;
        }

        public int Get(ProcessedFieldName fieldName)
        {
            switch (fieldName)
            {
                case ProcessedFieldName.CargoSpeedMin:
                    return CargoSpeedMin;
                case ProcessedFieldName.CarSpeedMin:
                    return CarSpeedMin;
                case ProcessedFieldName.CargoSpeedMax:
                    return CargoSpeedMax;
                case ProcessedFieldName.CarSpeedMax:
                    return CarSpeedMax;
                case ProcessedFieldName.CargoSpeedMean:
                    return CargoSpeedMean;
                case ProcessedFieldName.CarSpeedMean:
                    return CarSpeedMean;
                case ProcessedFieldName.CargoCount:
                    return CargoCount;
                case ProcessedFieldName.CarCount:
                    return CarCount;
                case ProcessedFieldName.CargoLength:
                    return (int)CargoLength;
                default:
                    return 0;
            }
        }
    }

    public enum ProcessedFieldName
    {
        CargoSpeedMin,
        CarSpeedMin,
        CargoSpeedMax,
        CarSpeedMax,
        CargoSpeedMean,
        CarSpeedMean,
        CargoCount,
        CarCount,
        CargoLength
    }
}