using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.VisualBasic;

namespace LamProcessor
{
    class Program
    {
        private static readonly string InputDataPath = @"YOUR_PATH\data\raw_data\";
        private static readonly string ExternalPath = @"YOUR_PATH\data\";
        
        static void Main(string[] args)
        {
            var lamIndexer = new LamIdIndexer();
            
            var years = new int[4] {2016, 2017, 2020, 2021};
            
            foreach (var year in years)
            {
                var days = DateTime.IsLeapYear(year) ? 366 : 365;
                for (var day = 1; day < days + 1; day++)
                {
                    var filePath = GetImagePath(year, day,
                        "CargoSpeedMax_day_DAY_yearYEAR_interval5_greyscale.bmp");
                    var bitmap = new Bitmap(filePath);
                    
                    var data = bitmap.LockBits(new Rectangle(0, 0, bitmap.Width, bitmap.Height), 
                        ImageLockMode.WriteOnly, PixelFormat.Format8bppIndexed);
                    
                    var bytes = new byte[data.Height * data.Stride];
                    Marshal.Copy(data.Scan0, bytes, 0, bytes.Length);

                    for (var i = 0; i < 55; i++)
                    {
                        var lamId = LamIndex.POHJANMAA_IDS[i];
                        var path = TryGetRawDataPath(year, day, 10, lamId);

                        if (!String.IsNullOrEmpty(path))
                        {
                            (var dir1Col, var dir2Col) = CreateDataColumns(path, 5);

                            var dir1Data = CreateBytePixelColumn(dir1Col, ProcessedFieldName.CargoSpeedMax);
                            var dir2Data = CreateBytePixelColumn(dir2Col, ProcessedFieldName.CargoSpeedMax);
                            (var dir1Index, var dir2Index) = lamIndexer.GetIndicesForDirections(lamId);
                            
                            var dir1IsEmpty = dir1Data.All(val => val == 0);
                            var dir1HadFaultyRows = dir1Col.Any(d => d != null && d.HadFaultyRows);
                            var dir2IsEmpty = dir2Data.All(val => val == 0);
                            var dir2HadFaultyRows = dir2Col.Any(d => d != null && d.HadFaultyRows);

                            WriteColumnOfData(bytes, dir1Data, data.Stride, dir1Index, dir1IsEmpty, dir1HadFaultyRows);
                            WriteColumnOfData(bytes, dir2Data, data.Stride, dir2Index, dir2IsEmpty, dir2HadFaultyRows);
                        } 
                    }

                    Marshal.Copy(bytes, 0, data.Scan0, bytes.Length);
                    
                    var savePath = $"{ExternalPath}\\processed_image_files_v3\\{year}\\{day}";
                    bitmap.UnlockBits(data);
                    CreateDirIfItDoesNotExist(savePath);
                    bitmap.Save($"{savePath}\\CargoSpeedMax_day_{day}_year{year}_interval5_greyscale.bmp");
                    
                    Console.WriteLine($"Day {day} done!");
                }
            }
        }

        private static string TryGetRawDataPath(int year, int dayNumber, int ely, int lamId)
        {
            var yrShort = year.ToString().Substring(2);
            var filePath = $"{InputDataPath}{year}\\{ely}\\lamraw_{lamId}_{yrShort}_{dayNumber}.csv";
            return File.Exists(filePath) ? filePath : "";
        }

        private static string GetImagePath(int year, int day, string imgTemplate)
        {
            var basePath = $"{ExternalPath}\\processed_image_files_v2\\{year}\\{day}\\";
            imgTemplate = imgTemplate.Replace("DAY", day.ToString());
            imgTemplate = imgTemplate.Replace("YEAR", year.ToString());

            return basePath + imgTemplate;
        }

        private static void WriteColumnOfData(byte[] bytes, byte[] toWrite, int stride, int col, bool isEmpty, bool faulty)
        {
            for (var i = 0; i < 288; i++)
                bytes[i * stride + col] = toWrite[i];
            
            bytes[288 * stride + col] = (byte)(isEmpty ? 255 : 0);
            bytes[289 * stride + col] = (byte)(isEmpty || faulty ? 255 : 0);
        }
        
        // static void Main(string[] args)
        // {
        //     Console.WriteLine("Starting execution");
        //     var timer = new Timer();
        //     timer.Start();
        //     
        //     var selectedYear = 2016;
        //     var selectedMinuteInterval = 5;
        //     var startDay = 1;
        //     Console.WriteLine("Starting to read available files");
        //     var files = GetAvailableFiles(InputDataPath, selectedYear);
        //     timer.Stop("reading available files");
        //
        //     timer.Start();
        //     var daysInSelectedYear = DateTime.IsLeapYear(selectedYear) ? 366 : 365;
        //
        //     var processingTimer = new Timer();
        //     processingTimer.Start();
        //     
        //     for (var i = startDay; i <= daysInSelectedYear; i++)
        //     {
        //         var data = ProcessLamDataFiles(files, selectedYear, i, selectedMinuteInterval);
        //
        //         SaveToBitMaps(data, i, selectedYear, selectedMinuteInterval);
        //
        //         Console.WriteLine($"{i}th day processed.");
        //         if (i % 10 == 0)
        //         {
        //             processingTimer.Stop("processing ten days of files");
        //             processingTimer.Start();
        //         }
        //     }
        //
        //     processingTimer.Stop();
        //     timer.Stop("processing all files");
        // }

        private static void SaveToBitMaps(ProcessedLamData[][] data, int dayNumber, int year, int interval)
        {
            var dataLength = data.Length;
            var rowCount = data[0].Length;
            var fieldNames = Enum.GetValues<ProcessedFieldName>();
            var savePath = $"{ExternalPath}\\processed_image_files_v2\\{year}\\{dayNumber}";

            CreateDirIfItDoesNotExist(savePath);
            // parallelOptions: new ParallelOptions{MaxDegreeOfParallelism = 1}, FOR EASIER DEBUGGING
            Parallel.ForEach(fieldNames, new ParallelOptions{MaxDegreeOfParallelism = 1 },  field =>
            {
                var rowCountWithExtraInfo = rowCount + 2; // We add empty and faulty info here
                var fieldString = field.ToString();
                var bm = new BitMapper(dataLength, rowCountWithExtraInfo);

                var byteMatrix = new byte[dataLength * (rowCountWithExtraInfo)];

                for (var i = 0; i < dataLength; i++)
                {
                    var isEmpty = data[i] == null;

                    if (!isEmpty)
                    {
                        var bytes = CreateBytePixelColumn(data[i], field);

                        for (var j = 0; j < rowCount; j++)
                        {
                            byteMatrix[j * dataLength + i] = bytes[j];
                        }
                    }

                    byteMatrix[rowCount * dataLength + i] = (byte) (isEmpty ? 255 : 0);
                    byteMatrix[(rowCount + 1) * dataLength + i] =
                        (byte) (isEmpty ? 255 : data[i].Any(d => d != null && d.HadFaultyRows) ? 255 : 0);
                }

                var result = bm.CreateFromMatrix(byteMatrix);
                // TODO: We need to distinguish directions from each other...
                result.Save($"{savePath}\\{fieldString}_day_{dayNumber}_year{year}_interval{interval}_greyscale.bmp", ImageFormat.Bmp);
                // for (var i = 0; i < dataLength; i++)
                // {
                //     if (data[i] == null)
                //         continue;
                //     var col = CreatePixelColumn(data[i], field);
                //     bm.SetColumnPixels(i, col);
                // }

                //bm.Save($"{savePath}\\{fieldString}_day{dayNumber}_year{year}_interval{interval}.bmp");
            });
        }

        private static void CreateDirIfItDoesNotExist(string path)
        {
            Directory.CreateDirectory(path);
        }

        private static ProcessedLamData[][] ProcessLamDataFiles(Dictionary<int, List<string>[]> files, int selectedYear, 
            int selectedDay, int selectedMinuteInterval)
        {
            var numberOfLams = LamIndex.Indices.Length;
            // Size is 2*numberOfLams since each LAM has two directions
            var data = new ProcessedLamData[numberOfLams * 2][];

            var lamIndexer = new LamIdIndexer();

            if (files.TryGetValue(selectedYear, out var days))
            {
                var dayIndex = selectedDay - 1;
                var filePaths = days[dayIndex];
                Console.WriteLine($"Year {selectedYear} day {selectedDay} has {filePaths.Count} files");

                Parallel.ForEach(filePaths, new ParallelOptions{MaxDegreeOfParallelism = 1 },filePath => //, new ParallelOptions{MaxDegreeOfParallelism = 1 }
                {
                    var lamId = GetLamId(filePath);
                    // var erroredLamIds = new int[]{242, 828};
                    // if (!erroredLamIds.Contains(lamId))
                    // {
                        (var dir1Index, int dir2Index) = lamIndexer.GetIndicesForDirections(lamId);
                        (var dir1Col, var dir2Col) = CreateDataColumns(filePath, selectedMinuteInterval);
                        data[dir1Index] = dir1Col;
                        data[dir2Index] = dir2Col;
                    // }
                    // else
                    // {
                    //     Console.WriteLine($"Skipping file {filePath}");
                    // }
                });
            }

            return data;
        }

        // private static int[] CreatePixelColumn(ProcessedLamData[] data, ProcessedFieldName field)
        // {
        //     var dataLength = data.Length;
        //     var col = new int[dataLength + 1]; // We'll have the data + two rows to note faulty and empty days
        //     var hadFaulty = false;
        //         
        //     for (var i = 0; i < dataLength - 1; i++)
        //     {
        //         var dataPoint = data[i];
        //         if (dataPoint.HadFaultyRows)
        //         {
        //             hadFaulty = true;
        //         }
        //         col[i] = dataPoint != null ? dataPoint.Get(field) : 0;
        //     }
        //
        //     col[dataLength - 1] = hadFaulty ? 1 : 0;
        //
        //     return col;
        // }
        
        private static byte[] CreateBytePixelColumn(ProcessedLamData[] data, ProcessedFieldName field)
        {
            var dataLength = data.Length;
            var col = new byte[dataLength];

            for (var i = 0; i < dataLength; i++)
            {
                col[i] = (byte)(data[i] != null ? data[i].Get(field) : 0);
            }

            return col;
        }

        private static int GetLamId(string filePath)
        {
            return int.Parse(filePath.Split("_")[^3]);
        }

        private static int GetDayNumber(string filePath)
        {
            return int.Parse(filePath.Split("_")[3].Split(".")[0]);
        }
            
        public static (ProcessedLamData[], ProcessedLamData[]) CreateDataColumns(string lamDataPath, int minuteInterval)
        {
            var rowCount = 24 * 60 / minuteInterval;

            var processedDir1 = new ProcessedLamData[rowCount];
            var processedDir2 = new ProcessedLamData[rowCount];
            
            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = false,
                Delimiter = ";",
            };
            
            var lamId = GetLamId(lamDataPath);
            var dayNumber = GetDayNumber(lamDataPath);
            
            using (var reader = new StreamReader(lamDataPath))
            using (var csv = new CsvReader(reader, config))
            {
                var records = csv.GetRecords<LamData>();

                var currentTimeIndex = 0;
                var dataCollectorDirection1 = new LamDataCollector(lamId, 1, dayNumber);
                var dataCollectorDirection2 = new LamDataCollector(lamId, 2, dayNumber);
                
                foreach (var lamDataPoint in records)
                {
                    var lamTimeIndex = (lamDataPoint.Hour * 60 + lamDataPoint.Minute) / minuteInterval;
                    if (!lamDataPoint.Faulty)
                    {
                        if (lamTimeIndex > currentTimeIndex)
                        {
                            try
                            {
                                processedDir1[currentTimeIndex] = dataCollectorDirection1.GetResult();
                                processedDir2[currentTimeIndex] = dataCollectorDirection2.GetResult();

                                dataCollectorDirection1 = new LamDataCollector(lamId, 1, dayNumber);
                                dataCollectorDirection2 = new LamDataCollector(lamId, 2, dayNumber);
                                currentTimeIndex = lamTimeIndex;
                            }
                            catch (Exception e)
                            {
                                Console.WriteLine($"Error file {lamDataPath}");
                            }
                        }
                    }

                    if (lamDataPoint.Direction == 1)
                        dataCollectorDirection1.AddDataPoint(lamDataPoint);
                    else
                        dataCollectorDirection2.AddDataPoint(lamDataPoint);
                }

                
                processedDir1[currentTimeIndex] = dataCollectorDirection1.GetResult();
                processedDir2[currentTimeIndex] = dataCollectorDirection2.GetResult();

                
                return (processedDir1, processedDir2);
            }
        }

        public static Dictionary<int, List<string>[]> GetAvailableFiles(string dataRootFolder, int selectedYear)
        {
            var fileInfo = new Dictionary<int, List<string>[]>();
            
            var years = new List<string>(Directory.EnumerateDirectories(dataRootFolder));

            foreach (var yearPath in years)
            {
                if (int.TryParse(yearPath.Substring(yearPath.Length - 4), out var yearInt))
                {
                    if (yearInt != selectedYear)
                        continue;
                    fileInfo.Add(yearInt, new List<string>[366]);
                }
                else
                {
                    // Directory wasn't year directory (meaning it was prolly logging directory)
                    continue;
                }

                var elys = new List<string>(Directory.EnumerateDirectories(yearPath));

                var yearFileList = fileInfo.GetValueOrDefault(yearInt);
                foreach (var elyPath in elys)
                {
                    var files = Directory.GetFiles(elyPath);

                    foreach (var fileName in files)
                    {
                        var fileNameTrimmed = fileName.Substring(0, fileName.Length - 4);
                        var splitName = fileNameTrimmed.Split("_");
                        var dayNumber = int.Parse(splitName.Last());
                        var dayIndex = dayNumber - 1;

                        if (yearFileList[dayIndex] == null)
                        {
                            yearFileList[dayIndex] = new List<string>();
                        }
                        
                        yearFileList[dayIndex].Add(fileName);
                    }
                }
            }

            return fileInfo;
        }
    }
}