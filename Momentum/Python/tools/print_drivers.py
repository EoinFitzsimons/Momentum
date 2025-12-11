from services.persistence_sqlite import PersistenceSQLite

def main():
    db = PersistenceSQLite()
    drs = db.list_drivers()
    print('---DRIVERS IN DB---')
    for d in drs[:24]:
        print(d.id, getattr(d, 'name', None), getattr(d, 'name_locale', None))

if __name__ == '__main__':
    main()
