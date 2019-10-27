from sqlite3 import connect


async def db_call(ctx, sql, filtered=[]):
    try:
        db = connect('dnd.db')
        conn = db.cursor()
        conn.execute(sql, filtered)
        db.commit()
        return conn.fetchall()
    except Exception as e:
        print(e)
        await ctx.send("An error has occurred with this command, please try again. "
                       "If this error persists please report it to Punky.")
    finally:
        if db:
            db.close()