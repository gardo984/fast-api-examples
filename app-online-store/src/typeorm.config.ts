
import { TypeOrmModuleOptions } from '@nestjs/typeorm';

export const typeOrmConfig: TypeOrmModuleOptions = {
	type: "mariadb",
	host: "localhost",
	port: 3306,
	username: "root",
	password: "123456",
	database: "dbstore",
	entities:
		[
			"dist/**/*.entity{.ts,.js}"
		],
	synchronize: true
}
