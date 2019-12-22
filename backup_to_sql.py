import os
import glob
import gzip
import database as db
from collections import OrderedDict
from tqdm import tqdm


# Opens backup file in backups folder and creates row list
def readFile():
    backup_files = glob.glob('backups/*.backup')
    # get latest backup file
    latest_backup_file = max(backup_files, key=os.path.getctime)
    print(f'backup file: {latest_backup_file}')
    if latest_backup_file:
        myfile = gzip.open(latest_backup_file, 'rt', encoding='utf-8').read()
        rows = myfile.splitlines()
        return rows
    return False


def parseEntities():
    rows = readFile()
    if rows:
        entities = OrderedDict()
        entity_item = OrderedDict()
        entity_type = ''
        is_new_entity = False
        for row in rows:
            if row.startswith('$ENTITY:'):
                entity_item = OrderedDict()
                entity_type = row.replace('$ENTITY:', '')
                continue
            # End of entity attributes
            elif row == '$$':
                is_new_entity = True
            else:
                attribute = row.split(':')
                if len(attribute) == 2:
                    entity_item[attribute[0]] = attribute[1]
            # Append to dict if all entity attributes parsed
            if is_new_entity:
                is_new_entity = False
                if entity_type in entities.keys():
                    entities[entity_type].append(entity_item)
                else:
                    entities[entity_type] = [entity_item]
        return entities
    return False


# writes parsed entities to database
def writeEntities():
    if not os.path.isfile('databases/financisto.db'):
        db.createTables()
    entities = parseEntities()
    if entities:
        for entity_type, entity_list in entities.items():
            print(entity_type)
            # for item in entity_list:
            for item in tqdm(entity_list, desc=entity_type):
                values = tuple(item.values())
                fields = '", "'.join(item.keys())
                qrytxt = '?'
                for i in range(len(values)-1):
                    qrytxt = qrytxt + ', ' + '?'
                query = 'INSERT OR IGNORE INTO ' + entity_type + '("' + fields + '")' + ' VALUES ' + '(' + qrytxt + ')'
                db.writeQuery(values, query)


writeEntities()
