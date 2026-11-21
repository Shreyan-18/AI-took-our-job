import { defineConfig } from '@prisma/config';
import dotenv from 'dotenv';
dotenv.config();

export default defineConfig({
  schema: 'prisma/schema.prisma',
  datasource: {
    url: process.env.DATABASE_URL || "postgresql://neondb_owner:npg_hyM4FOuYc1pR@ep-bitter-bar-b3fdsiih-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
  },
});
