from telegram_geobot.db_handlers.geobot_mongodb import get_flag_emojis, mongo_db
from random import sample


FLAG_EMOJIS_PATH = 'telegram_geobot/emoji_handlers/emoji_data/flag_emojis.csv'
START_EMOJIS = ['🌏','🌍','🌎','🗺','🎆','🎇','🌆','🌃','🌁','🌉']

def write_flag_emojis():
    '''Write to csv file all emojis of flags so don't to query them all the time. There are only 25'''
    flag_emojis = get_flag_emojis(mongo_db)
    with open(FLAG_EMOJIS_PATH, 'w') as f:
        data = ','.join(flag_emojis)
        f.write(data)


def get_n_random_flags(n: int) -> list:
    with open(FLAG_EMOJIS_PATH, 'r') as f:
        data = f.read()
        all_flags = data.split(',')
        flags_sample = sample(all_flags, n)
        return flags_sample

if __name__ == '__main__':
    
    random_flags = get_n_random_flags(5)
    for f in random_flags: 
        print(f)

    print('Hello world!')


