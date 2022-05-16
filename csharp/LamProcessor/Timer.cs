using System;
using System.Diagnostics;

namespace LamProcessor
{
    public class Timer
    {
        private readonly Stopwatch _watch = new Stopwatch();

        public void Start()
        {
            _watch.Reset();
            _watch.Start();
        }

        public void Stop(string taskName = "")
        {
            _watch.Stop();
            
            Console.WriteLine($"Done {taskName} in {_watch.ElapsedMilliseconds} ms");
            Console.WriteLine("");
        }
    }
}