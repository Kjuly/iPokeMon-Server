#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import sys, os
from subprocess import Popen, PIPE
import datetime


GENERATED_FILE_NAME = 'generated_file'

# Generate a same name list with a number range
#   $ python utility.py 1 <int:number>
if sys.argv[1] == '1':
    cmd = Popen(['touch', GENERATED_FILE_NAME])
    cmd = open(GENERATED_FILE_NAME, 'w')
    for num in range(1, int(sys.argv[2]) + 1):
        #line = '"PMSAbilityInfo%.3d" = \n' % num
        #line = 'http://www.pokemonelite2000.com/sprites/bwb/%d.png\n' % num
        line = '%d\n' % num
        cmd.write(str(line))
    cmd.close()

# Sort file based on word, |argv[2]| as the file name
#   $ python utility.py 2 target_file
elif sys.argv[1] == '2':
    lines = open(sys.argv[2]).readlines()
    lines.sort()
    new_file = open(GENERATED_FILE_NAME, 'w')
    new_file.writelines(lines)
    new_file.close()

# Insert new elements to original xml file
#   $ python utility.py 3 target_file new_data_file
elif sys.argv[1] == '3':
    #import xml.etree.cElementTree as ElemTree
    import xml.etree.ElementTree as ElemTree

    # New Data Lines
    new_data_lines = open(sys.argv[3]).readlines()
    # XML Element Tree
    tree = ElemTree.ElementTree(file=sys.argv[2])

    i = 0
    apped_to_next = False
    for elem in tree.getiterator():
        # Find the last one in <dict>, and add white space to |tail|,
        # so the new element will have an indentation.
        if elem.tag == 'key' and elem.text == 'effectCode':
            apped_to_next = True
            continue
        if apped_to_next:
            elem.tail = '\n' + '    '
            apped_to_next = False

        # Only append new element to <dict>
        if not elem.tag == 'dict':
            continue

        new_elem_key        = ElemTree.Element('key')
        new_elem_key.text   = 'target'
        new_elem_key.tail   = '\n' + '    '
        new_elem_value      = ElemTree.Element('integer')
        new_elem_value.text = new_data_lines[i][:-1]
        new_elem_value.tail = '\n' + '  '

        elem.append(new_elem_key)
        elem.append(new_elem_value)
        i += 1
    # Save the new generated file
    tree.write(GENERATED_FILE_NAME)


# Modify elements in original xml file
#   $ python utility.py 4 target_file new_data_file
elif sys.argv[1] == '4':
    #import xml.etree.cElementTree as ElemTree
    import xml.etree.ElementTree as ElemTree

    # Constants
    ORIGINAL_FILE = sys.argv[2]
    # New Data Lines
    new_data_lines = open(sys.argv[3]).readlines()
    # XML Element Tree
    tree = ElemTree.ElementTree(file=ORIGINAL_FILE)

    i = 0
    modify_for_next = False
    for elem in tree.getiterator():
        # Find the last one in <dict>, and add white space to |tail|,
        # so the new element will have an indentation.
        if elem.tag == 'key' and elem.text == 'type':
            modify_for_next = True
            continue
        if modify_for_next:
            elem.text = new_data_lines[i][:-1]
            i += 1
            modify_for_next = False
    # Save the new generated file
    tree.write(GENERATED_FILE_NAME)

# Copy part of file
#   $ python utility.py 5 target_file
elif sys.argv[1] == '5':
    old_data_lines = open(sys.argv[2]).readlines()
    new_file       = open(GENERATED_FILE_NAME, 'w')
    i = 1
    for line in old_data_lines:
        if i % 4 == 1:
            new_file.write(line)
        i += 1
    new_file.close()

# Filiter data dependent on given string file
#   $ python utility.py 6 target_file filiter_string_file
elif sys.argv[1] == '6':
    old_data_lines = open(sys.argv[2]).readlines()
    filiters       = open(sys.argv[3]).readlines()
    new_file       = open(GENERATED_FILE_NAME, 'w')

    copy_next_line = False
    for line in old_data_lines:
        if copy_next_line:
            new_file.write(line)
            copy_next_line = False
            continue
        # If the name exists in filiters, copy next data line
        for filiter_name in filiters:
            if str(line).lower() == str(filiter_name).lower():
                copy_next_line = True
                break
    new_file.close()

# Filiter data dependent on given string file (in order) - v2
#   $ python utility.py 61 target_file filiter_string_file line_number
elif sys.argv[1] == '61':
    old_data_lines = open(sys.argv[2]).readlines()
    filiters       = open(sys.argv[3]).readlines()
    line_number    = int(sys.argv[4])
    new_file       = open(GENERATED_FILE_NAME, 'w')

    copy_next_line = 0
    for filiter_name in filiters:
        for line in old_data_lines:
            if copy_next_line:
                new_file.write(line)
                copy_next_line -= 1
                continue
            # If the name exists in filiters, copy next data lines
            if str(line).lower() == str(filiter_name).lower():
                new_file.write(line)
                copy_next_line = line_number
    '''
    copy_next_line = 0
    for line in old_data_lines:
        if copy_next_line:
            new_file.write(line)
            copy_next_line -= 1
            continue
        # If the name exists in filiters, copy next data line
        for filiter_name in filiters:
            if str(line).lower() == str(filiter_name).lower():
                #print(line)
                print(filiter_name[:-1])
                new_file.write(line)
                copy_next_line = line_number
                break
    '''
    new_file.close()

# Generate a file for Wget to fetch batch url page
#   $ python utility.py 7 url_root url_parts_file
elif sys.argv[1] == '7':
    url_parts = open(sys.argv[3]).readlines()
    URL_ROOT  = sys.argv[2]
    new_file  = open(GENERATED_FILE_NAME, 'w')

    for url_part in url_parts:
        url = '%s/%s' % (URL_ROOT, str(url_part).lower())
        new_file.write(url)
        #cmd = Popen(['wget', url])
    new_file.close()

# Copy multiple file to one
#   $ python utility.py 8 files_name
elif sys.argv[1] == '8':
    files_name = open(sys.argv[2]).readlines()
    new_file   = open(GENERATED_FILE_NAME, 'w')
    for file_name in files_name:
        #print(str(file_name)[:-1].lower())
        old_file = open(str(file_name)[:-1].lower()).readlines()
        for line in old_file:
            new_file.write(line)
    new_file.close()

# Replace words to number in file
#   $ python utility.py 9 target_file words_file
elif sys.argv[1] == '9':
    import re
    old_file = open(sys.argv[2])
    #old_file = open(sys.argv[2]).readlines()
    words    = open(sys.argv[3]).readlines()
    new_file = open(GENERATED_FILE_NAME, 'w')

    for line in old_file:
        i = 1
        new_line = line
        for word in words:
            regular = re.compile(str(word[:-1]).lower())
            new_line = regular.sub(str(i), str(new_line).lower())
            i += 1
        new_file.write(new_line)
    new_file.close()





'''
# Find the key not exists in filiter file
#   $ python utility.py 6 target_file filiter_string_file
elif sys.argv[1] == '7':
    old_data_lines = open(sys.argv[2]).readlines()
    filiters       = open(sys.argv[3]).readlines()

    key_exists = False
    for line in old_data_lines:
        key_exists = False
        for filiter_name in filiters:
            if str(line).lower() == str(filiter_name).lower():
                key_exists = True
                break
        if key_exists:
            continue
        print(line)
'''

'''
kFileOldHosts           = '/etc/hosts'
kFileNewHosts           = 'hosts'
kFilePatch              = 'hosts.patch'
kDirForOldHostsBackup   = './backup'

# Backup the old hosts to |kDirForOldHostsBackup| with date
date_string = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
cmd_cp = Popen(['cp', kFileOldHosts, kDirForOldHostsBackup + '/hosts_' + date_string])

# Analyze the difference between ole & new hosts
cmd_diff = Popen(['diff', 'hosts', kFileOldHosts], stdout=PIPE)
output_diff = cmd_diff.communicate()[0]

# Generate a patch file for old hosts depend on the new hosts
patch_process = open(kFilePatch, 'w')
patch_process.writelines(output_diff)
patch_process.close()

# Apply the patch to the old hosts
cmd_patch = Popen(['patch', '-Rp0', kFileOldHosts, kFilePatch])
'''
