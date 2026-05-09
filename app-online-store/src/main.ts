import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { NestExpressApplication } from '@nestjs/platform-express';
import hbs from 'hbs';
import hbsUtils from 'hbs-utils';
import { join } from 'path';

async function bootstrap() {
  /*const app = await NestFactory.create(AppModule);*/
  const app = await NestFactory.create<NestExpressApplication>(
    AppModule
  );
  app.useStaticAssets(join(__dirname, '..', 'public'));
  app.setBaseViewsDir(join(__dirname, '..', 'views'));
  const layoutsPath = join(__dirname, '..', 'views/layouts');
  hbs.registerPartials(layoutsPath);
  hbsUtils(hbs).registerWatchedPartials(layoutsPath);
  app.setViewEngine('hbs')
  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
