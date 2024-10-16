from typing import Union

import asyncpg
from asyncpg import Pool, Connection

from tgbot.config import load_config

config = load_config(".env")


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database,
            max_inactive_connection_lifetime=3
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):

        async with self.pool.acquire() as connection:
            connection: Connection()
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Salaam_users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        telegram_id BIGINT NOT NULL UNIQUE, 
        number BIGINT NOT NULL,
        language VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    @staticmethod
    def format_args2(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=2)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, telegram_id, number, language):
        sql = "INSERT INTO Salaam_users (full_name, telegram_id, number, language) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, full_name, telegram_id, number, language, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Salaam_users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Salaam_users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_user(self, telegram_id, **kwargs):
        sql = "UPDATE Salaam_users SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f" WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, *parameters, execute=True)

    async def count_users(self):
        return await self.execute("SELECT COUNT(*) FROM Salaam_users;", fetchval=True, execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Salaam_users", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Salaam_admins (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE, 
        name VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_administrator(self, telegram_id, name):
        sql = "INSERT INTO Salaam_admins (telegram_id, name) VALUES ($1, $2) returning *"
        return await self.execute(sql, telegram_id, name, fetchrow=True)

    async def select_all_admins(self):
        sql = "SELECT * FROM Salaam_admins"
        return await self.execute(sql, fetch=True)

    async def select_id_admins(self):
        sql = "SELECT telegram_id FROM Salaam_admins"
        return await self.execute(sql, fetch=True)

    async def select_admin(self, **kwargs):
        sql = "SELECT * FROM Salaam_admins WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def delete_admin(self, telegram_id):
        await self.execute("DELETE FROM Salaam_admins WHERE telegram_id=$1", telegram_id, execute=True)

    async def drop_admins(self):
        await self.execute("DROP TABLE Salaam_admins", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_flights(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Salaam_flights (
        id SERIAL PRIMARY KEY,
        city VARCHAR(255) NOT NULL,
        year INT NOT NULL,
        month INT NOT NULL,
        number_of_dates INTEGER[] NULL,
        econom TEXT NULL,
        standart TEXT NULL,
        vip TEXT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_flight(self, city, year, month, number_of_dates, econom, standart, vip):
        sql = "INSERT INTO Salaam_flights (city, year, month, number_of_dates, econom, standart, vip) VALUES ($1, $2, $3, $4, $5, $6, $7) returning *"
        return await self.execute(sql, city, year, month, number_of_dates, econom, standart, vip, fetchrow=True)

    async def select_all_flights(self):
        sql = "SELECT * FROM Salaam_flights"
        return await self.execute(sql, fetch=True)

    async def select_flights(self, **kwargs):
        sql = "SELECT * FROM Salaam_flights WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_flight(self, **kwargs):
        sql = "SELECT * FROM Salaam_flights WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_flight(self, id, **kwargs):
        sql = "UPDATE Salaam_flights SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f" WHERE id=$1"
        return await self.execute(sql, id, *parameters, execute=True)

    async def delete_flight(self, id):
        await self.execute("DELETE FROM Salaam_flights WHERE id=$1", id, execute=True)

    async def drop_flights(self):
        await self.execute("DROP TABLE Salaam_flights", execute=True)



    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_referral(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Referral (
        id SERIAL PRIMARY KEY,
        referrer BIGINT NOT NULL,
        referral BIGINT NOT NULL 
        );
        """
        await self.execute(sql, fetch=True)

    async def add_referral(self, referrer, referral):
        sql = "INSERT INTO Referral (referrer, referral) VALUES($1, $2) returning *"
        return await self.execute(sql, referrer, referral, fetchrow=True)

    async def select_referral(self, referral):
        sql = "SELECT * FROM Referral WHERE referral=$1"
        return await self.execute(sql, referral, fetch=True)

    async def select_all_referrers(self):
        sql = "SELECT * FROM Referral"
        return await self.execute(sql, fetch=True)

    async def count_referrals(self, referrer):
        sql = "SELECT COUNT(*) FROM Referral WHERE referrer=$1"
        return await self.execute(sql, referrer, fetchval=True)

    async def delete_referral(self, referral):
        sql = "DELETE FROM Referral WHERE referral=$1"
        return await self.execute(sql, referral, execute=True)

    async def drop_referral(self):
        await self.execute("DROP TABLE Referral", execute=True)