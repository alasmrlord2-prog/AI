//@ts-check

'use strict';

const withDefaults = require('../../shared.webpack.config');

module.exports = withDefaults({
	context: __dirname,
	entry: {
		main: './src/main.ts',
	},
	plugins: [], // no default copy
});
