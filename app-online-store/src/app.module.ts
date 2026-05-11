import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { ProductsController } from './products.controller';
import {
  TypeOrmModule
} from '@nestjs/typeorm';
import { typeOrmConfig } from './typeorm.config';
import { ProductsService } from './models/products.service';
import { Product } from './models/products.entity';
import { TypeORMError } from 'typeorm';

@Module({
  imports: [
    TypeOrmModule.forRoot(typeOrmConfig),
    TypeOrmModule.forFeature([Product,]),
  ],
  controllers: [AppController, ProductsController],
  providers: [
    ProductsService,
  ],
})
export class AppModule {}
