using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

namespace LamProcessor
{
    public class BitMapper
    {
        private readonly System.Drawing.Bitmap _map;

        public BitMapper(int width, int height)
        {
            _map = new Bitmap(width, height, PixelFormat.Format8bppIndexed);
        }
        
        public BitMapper(Bitmap bm)
        {
            _map = bm;
        }

        public void SetColumnPixels(int colIndex, int[] pixels)
        {
            var pixelCount = pixels.Length;
            for (var i = 0; i < pixelCount; i++)
            {
                var pixelVal = pixels[i];
                
                _map.SetPixel(colIndex, i, Color.FromArgb(pixelVal, pixelVal, pixelVal));
            }
        }

        public void Save(string path)
        {
            _map.Save(path, ImageFormat.Bmp);
        }

        public Bitmap CreateFromMatrix(byte[] matrix)
        {
            var data = _map.LockBits(new Rectangle(0, 0, _map.Width, _map.Height), ImageLockMode.WriteOnly, 
                PixelFormat.Format8bppIndexed);
            var scan0 = data.Scan0.ToInt64();

            for (var x = 0; x < _map.Width; x++)
                Marshal.Copy(matrix, x * _map.Height, new IntPtr(scan0 + x * _map.Height), _map.Height);

            
            _map.UnlockBits(data);
            // Get the original palette. Note that this makes a COPY of the ColorPalette object.
            var pal = _map.Palette;
            
            // Generate grayscale colours:
            for (var i = 0; i < 256; i++)
                pal.Entries[i] = Color.FromArgb(i, i, i);
            // Assign the edited palette to the bitmap.
            _map.Palette = pal;
            return _map;
        }
    }
}