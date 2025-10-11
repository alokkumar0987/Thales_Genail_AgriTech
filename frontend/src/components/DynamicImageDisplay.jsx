import React from 'react';

const DynamicImageDisplay = ({ images }) => {
  return (
    <div className="flex items-center space-x-4 overflow-hidden">
      {images.map((src, index) => (
        <div
          key={index}
          className="relative w-24 h-24 sm:w-28 sm:h-28 lg:w-32 lg:h-32 transform rotate-45 overflow-hidden shadow-md"
          style={{
            minWidth: '6rem',
            minHeight: '6rem',
            marginLeft: index > 0 ? '-30px' : '0',
          }}
        >
          <img
            src={src}
            alt={`Agricultural scene ${index + 1}`}
            className="absolute inset-0 w-full h-full object-cover transform -rotate-45 scale-125"
          />
        </div>
      ))}
    </div>
  );
};

export default DynamicImageDisplay;