import psycopg2 as pc2


class Database():
    def __init__(self):
        self.connection = pc2.connect(
            user="postgres",
            password="205896",
            host="127.0.0.1",
            port="5432",
            database="Spirtokiada"
        )
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT version();")
        print(f"Вы подключены к - {self.cursor.fetchone()}")

    # Add people to database. Registration
    async def create_player(self, nickname='None', first_name='None', last_name='None', employee=False, tg_id=0,
                            chat_id=0):
        query = f"""SELECT 
                                COUNT(users.user_id),
                                team.team_id
                            FROM
                                users INNER JOIN team on team.team_id = users.team_id
                            GROUP BY
                                team.team_id
                            ORDER BY
                                COUNT(users.user_id) ASC"""
        self.cursor.execute(query)
        team = self.cursor.fetchone()[1]

        self.cursor.execute(f"""INSERT INTO users (nickname, first_name, last_name, employee, tg_id, chat_id, team_id)
                        VALUES ('{nickname}', '{first_name}', '{last_name}', {employee}, {tg_id}, {chat_id}, {team}) """)
        self.connection.commit()

        self.cursor.execute(f"""SELECT
                                    team_name
                                FROM
                                    team
                                Where
                                    team_id = {team}""")
        team_name = self.cursor.fetchone()[0]
        return team_name

    # Get user_id from tg_id
    async def get_user_id(self, tg_id='None'):
        self.cursor.execute(f"""SELECT
                                    public.users.user_id,
                                    public.users.tg_id
                                FROM
                                    public.users
                                WHERE
                                    public.users.tg_id={tg_id}""")
        id = self.cursor.fetchone()
        return id[0]

    async def show_rating(self, tg_id='None'):
        self.cursor.execute(f"""select rating, points from (Select ROW_NUMBER() OVER(Order by public.users.points desc) as rating,
                                nickname, points, tg_id From
                                    public.users) as a
                                where tg_id = {tg_id}""")

        rating = (self.cursor.fetchone())
        return f"На данный момент вы занимаете <u><b>{rating[0]}</b></u> место!\nКол-во очков: <b>{rating[1]}</b>"

    async def show_ticket(self, tg_id='None'):
        self.cursor.execute(f"""Select
                                public.ticket.ticket_id,
                                public.game.name_game,
                                public.users.tg_id,
                                public.ticket.is_active
                            from
                                public.ticket
                                INNER JOIN public.game on public.ticket.game_id = public.game.game_id
                                INNER JOIN public.users on public.ticket.user_id = public.users.user_id
                            WHERE
                                public.users.tg_id = {tg_id} AND public.ticket.is_active = TRUE""")

        tickets = self.cursor.fetchall()

        return tickets

    async def check_employee(self, tg_id='None'):
        self.cursor.execute(f"""select tg_id, employee
                            from users
                            where tg_id = {tg_id} and employee = true""")
        employee = self.cursor.fetchone()
        return employee

    # Check existence person
    async def check_person(self, user_id='None'):
        self.cursor.execute(f"""select 
                                    user_id
                                from
                                    users
                                where
                                    user_id = {user_id}""")
        person = self.cursor.fetchone()
        return person

    async def add_new_ticket(self, user_id='None', game_id='None'):
        self.cursor.execute(f"""INSERT INTO ticket (game_id, user_id, is_active) VALUES ({game_id}, {user_id}, true)""")
        self.connection.commit()

    def show_game_list(self):
        self.cursor.execute(f"""SELECT game_id, name_game FROM public.game
                                ORDER BY game_id ASC """)
        game_list = self.cursor.fetchall()
        return game_list

    async def set_zone_technic(self, game_id='None', user_id='None'):
        self.cursor.execute(f"""INSERT INTO technic (user_id, game_id) VALUES ({user_id}, {game_id})""")
        self.connection.commit()

    # For game_Technic
    async def get_active_tickets(self, tg_id='None'):
        technic = await self.get_user_id(tg_id=tg_id)

        self.cursor.execute(f"""Select
                                user_id,
                                game_id
                            from
                                public.technic
                            where
                                user_id={technic}""")
        game_id = self.cursor.fetchone()
        self.cursor.execute(f"""SELECT
                              ticket_id,
                              game_id,
                              user_id,
                              is_active
                          FROM
                              public.ticket
                          WHERE
                              game_id={game_id[1]} and is_active=true
                          ORDER BY
                              ticket_id ASC""")
        ticket_list = self.cursor.fetchall()
        return ticket_list

    async def set_false_ticket(self, ticket_id):
        self.cursor.execute(f"""update public.ticket
                                set is_active = false
                                where ticket_id = {ticket_id}""")
        self.connection.commit()

    async def get_user_points(self, user_id):
        self.cursor.execute(f"""select user_id, points
                                from users
                                where user_id = {user_id}""")
        points = self.cursor.fetchone()[1]
        return points

    async def set_points_to_user(self, user_id, points, add_points):
        points += int(add_points)
        self.cursor.execute(f"""update users
                                        set points = {points}
                                        where user_id = {user_id}""")
        self.connection.commit()





    async def get_team_points(self, tg_id):
        query = f"SELECT team_id FROM users WHERE tg_id = {tg_id}"
        self.cursor.execute(query)
        team_id = self.cursor.fetchone()[0]

        query = f"SELECT points FROM team WHERE team_id = {team_id}"
        self.cursor.execute(query)
        team_points = self.cursor.fetchone()[0]

        return team_points, team_id

    async def get_team_rating(self, tg_id):
        team_points, team_id = await self.get_team_points(tg_id)
        query = f"""select
                        place
                    from
                        (select
                        ROW_NUMBER() OVER(ORDER BY points DESC) as place,
                        team_name,
                        team_id
                        from
                         team
                        ) as a
                    where
                        team_id = {team_id}"""
        self.cursor.execute(query)
        place = self.cursor.fetchone()[0]
        text = f"Ваша команда имеет <b>{team_points}</b> очков и занимает <b>{place}</b> место!"
        return text

    async def set_points_to_team(self, tg_id, points):
        team_points, team_id = await self.get_team_points(tg_id)
        team_points += points

        query = f"UPDATE team SET points={team_points} WHERE team_id={team_id}"
        self.cursor.execute(query)
        self.connection.commit()

    async def get_all_tickets(self):
        self.cursor.execute(f"""SELECT
                                      ticket_id,
                                      game_id,
                                      user_id,
                                      is_active
                                  FROM
                                      public.ticket
                                  ORDER BY
                                      ticket_id ASC""")
        ticket_list = self.cursor.fetchall()
        return ticket_list

    async def get_raiting(self):
        self.cursor.execute(f"""SELECT user_id, first_name, last_name, points FROM public.users
                            ORDER BY points DESC""")
        raiting = self.cursor.fetchall()
        return raiting
