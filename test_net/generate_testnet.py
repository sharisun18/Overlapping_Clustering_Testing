#!/usr/bin/env python
# encoding: utf-8

import sys
import re


if __name__ == '__main__':

	with open('24_testnet_3c0o_2100_nodes', 'w') as wf:

		for start in range(0,700):
			for end in range(start+1,700):
				wf.write(str(start) + ' ' + str(end) + '\n')

		for start in range(700,1400):
			for end in range(start+1,1400):
				wf.write(str(start) + ' ' + str(end) + '\n')

		for start in range(1400,2100):
			for end in range(start+1,2100):
				wf.write(str(start) + ' ' + str(end) + '\n')
		
		wf.write(str(2101) + ' ' + str(2) + '\n' )
		wf.write(str(2101) + ' ' + str(2102) + '\n')

		wf.write(str(2102) + ' ' + str(803) + '\n')
		wf.write(str(2102) + ' ' + str(2103) + '\n')
		
		wf.write(str(2103) + ' ' + str(576) + '\n' )
		wf.write(str(2103) + ' ' + str(2107) + '\n')
		
		wf.write(str(2104) + ' ' + str(234) + '\n' )
		wf.write(str(2104) + ' ' + str(2105) + '\n')
		wf.write(str(2104) + ' ' + str(2107) + '\n')

		wf.write(str(2105) + ' ' + str(1586) + '\n')

		wf.write(str(2106) + ' ' + str(958) + '\n')
		wf.write(str(2106) + ' ' + str(2107) + '\n')

		wf.write(str(2107) + ' ' + str(1285) + '\n')
		wf.write(str(2107) + ' ' + str(2048) + '\n')

		wf.write(str(2108) + ' ' + str(1288) + '\n')

		wf.write(str(2109) + ' ' + str(1486) + '\n')


