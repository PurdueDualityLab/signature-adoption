#!/usr/bin/env python

'''number_things.py This script helps do some number manipulation stuff.'''

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


def human_format(num):
    '''
    This function is used to convert a number to a human readable format.
    '''
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def pc_str(num, denom=1, precision=1):
    '''
    This function is used to calculate the percentage of num/denom.

    num: The numerator of the fraction.
    denom: The denominator of the fraction.

    returns: The percentage of num/denom as a string.
    '''
    if denom == 0:
        return '0.' + '0'*precision + '%'
    format_str = f'{{:.{precision}f}}%'
    return format_str.format(100 * num / denom)
