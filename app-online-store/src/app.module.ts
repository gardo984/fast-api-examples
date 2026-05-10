import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { ProductsController } from './products.controller';
import {
  TypeOrmModule
} from '@nestjs/typeorm';
import { typeOrmConfig } from './typeorm.config';
/*import { AppService } from './app.service';*/

@Module({
  imports: [TypeOrmModule.forRoot(typeOrmConfig),],
  controllers: [AppController, ProductsController],
  providers: [],
})
export class AppModule {}
