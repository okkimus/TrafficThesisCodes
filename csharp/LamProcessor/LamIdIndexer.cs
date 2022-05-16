using System;
using System.Collections.Generic;

namespace LamProcessor
{
    public class LamIdIndexer
    {
        private readonly Dictionary<int, int> _indices;

        public LamIdIndexer()
        {
            _indices = new Dictionary<int, int>();
            AddIndices();
        }

        public int GetIndex(int lamId)
        {
            if (_indices.TryGetValue(lamId, out var index))
            {
                return index;
            }
            else
            {
                throw new Exception($"Couldn't find index for lamId {lamId}");
            }
        }

        public int GetLamId(int index)
        {
            return LamIndex.Indices[index];
        }
        
        public int GetLamIdForPairedData(int index)
        {
            return GetLamId(index / 2);
        }

        public (int, int) GetIndicesForDirections(int lamId)
        {
            var index = GetIndex(lamId);
            return (index * 2, index * 2 + 1);
        }
        
        private void AddIndices()
        {
            for (var i = 0; i < LamIndex.Indices.Length; i++)
            {
                _indices.Add(LamIndex.Indices[i], i);
            }
        }
    }
}