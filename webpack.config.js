const path = require('path');
const fs = require('fs');

const fileNames = fs.readdirSync('./src').reduce((acc, cur) => {
  if (cur.endsWith(".ts") || cur.endsWith(".js")) {
    return [ ...acc, `./src/${cur}` ]; // return { ...acc, [cur]: `./src/${cur}` };
  }
  return acc;
}, []);

module.exports = {
  // entry: fileNames,
  entry: ['./src/index.ts'],
  module: {
    rules: [
      {
        test: /\.ts?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    filename: 'index.js',
    path: path.resolve(__dirname, 'dist'),
  },
  mode: 'production',
};