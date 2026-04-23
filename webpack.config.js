const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const VueLoaderPlugin = require('vue-loader/lib/plugin');

module.exports = {
  mode: 'development',
  context: __dirname,
  entry: './assets/js/index',
  output: {
    path: path.resolve('./assets/bundles/'),
    filename: 'app.js'
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new VueLoaderPlugin(),
  ],

  module: {
    rules:  [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.css$/,
        use: [
            'vue-style-loader',
            'css-loader'
        ]
      },
      {
        test: /\.scss$/,
        use: [
          {
            loader: "style-loader"
          },
          {
            loader: "css-loader"
          },
          {
            loader: "sass-loader",
            options: {
              includePaths: ['./assets/scss']
            }
          }
        ]
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [{
          loader: 'file-loader',
          options: {
            name: '[name].[ext]',
            outputPath: 'fonts/',
            publicPath: '/static/bundles/fonts'
          }
        }]
      },
    ],
  },

  resolve: {
    alias: {vue: 'vue/dist/vue.js'}
  },

  watchOptions: {
    aggregateTimeout: 300,
    poll: 1000,
    ignored: /node_modules/
  },
};
