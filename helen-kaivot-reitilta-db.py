# -*- coding: utf-8 -*-
import psycopg2, json, sys, argparse

host=""
database=""
user=""
password=""
port=""

def mapper( row ):
    return {
        "route_id": row[0],
        "route_nimi": row[1],
        "route_tunnus": row[2],
        "target_id": row[3],
        "target_nimi": row[4],
        "target_tunnus": row[5],
        "route_deleted": row[6],
        "route_targets_deleted": row[7],
        "target_deleted": row[8]
    }

def open_connection():
    return psycopg2.connect(host=host,
                            database=database, 
                            user=user, 
                            password=password, 
                            port=port)

def fetch_data( conn, tunnus ):
    sql = """select r.id,r.nimi,r.tunnus,t.id,t.nimi,t.tunnus,r.deleted,rt.deleted,t.deleted 
             from route r,route_targets rt, target t where rt.route_id = r.id and rt.target_id = t.id
              and r.tunnus = %s
              and rt.deleted = false
              order by t.tunnus; """

    result = None

    try:
        cur = conn.cursor()
        cur.execute(sql, (tunnus,))
        result = cur.fetchall()        
        return map(mapper, result)        
    except psycopg2.Error as e:
        print(e)

def print_json(data):
    result_string = json.dumps(data , sort_keys=True, 
                              indent=2, separators=(',', ': '))
    print(result_string)

def create_argparser():
    parser = argparse.ArgumentParser(description='Hae kaivot reitilta, reitin tunnusta vastaan.')
    parser.add_argument('-t', '--tunnus', dest='tunnus')
    return parser

def main(argv=sys.argv):
    argparser = create_argparser()

    if len(argv) == 1:
        argparser.print_help()
    else:    
        args = argparser.parse_args(argv[1:])
        conn = open_connection()
        data = fetch_data(conn, args.tunnus)
        print_json(data)

if __name__ == '__main__':
    main()
