#!/usr/bin/env node
/**
 * Perfect Text Overlay CLI
 * Command line interface for the perfect-text-overlay package
 */

const { program } = require('commander');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

const {
  separatePrompt,
  analyzeImage,
  renderTextOnImage,
  getTextPlacementSuggestions,
  checkPythonEnvironment
} = require('../lib/index');

const pkg = require('../package.json');

program
  .name('perfect-text-overlay')
  .description('Fix imperfect AI-generated text in images by separating image generation and text overlay')
  .version(pkg.version);

// Command: separate
program
  .command('separate')
  .description('Separate prompt into image-only prompt and text requirements')
  .requiredOption('-p, --prompt <prompt>', 'User prompt to separate')
  .option('-o, --output <file>', 'Output file for JSON result')
  .action(async (options) => {
    try {
      console.log(chalk.blue('📝 Separating prompt...'));
      console.log(chalk.gray(`Input: ${options.prompt}`));

      const result = await separatePrompt(options.prompt);

      console.log(chalk.green('✅ Prompt separated successfully!'));
      console.log(chalk.cyan('\n📷 Image Prompt:'));
      console.log(result.image_prompt);

      if (result.has_text) {
        console.log(chalk.cyan('\n📋 Text Requirements:'));
        console.log(JSON.stringify(result.text_requirements, null, 2));
      }

      if (options.output) {
        fs.writeFileSync(options.output, JSON.stringify(result, null, 2));
        console.log(chalk.green(`\n💾 Result saved to: ${options.output}`));
      }
    } catch (error) {
      console.error(chalk.red('❌ Error:'), error.message);
      process.exit(1);
    }
  });

// Command: analyze
program
  .command('analyze')
  .description('Analyze image for text placement')
  .requiredOption('-i, --image <path>', 'Path to input image')
  .requiredOption('-r, --requirements <json>', 'Text requirements JSON string or file path')
  .option('-o, --output <file>', 'Output file for JSON result')
  .action(async (options) => {
    try {
      console.log(chalk.blue('🔍 Analyzing image...'));
      console.log(chalk.gray(`Image: ${options.image}`));

      let requirements;
      try {
        // Try to parse as JSON string first
        requirements = JSON.parse(options.requirements);
      } catch {
        // Try to read as file
        if (fs.existsSync(options.requirements)) {
          requirements = JSON.parse(fs.readFileSync(options.requirements, 'utf8'));
        } else {
          throw new Error('Requirements must be valid JSON string or file path');
        }
      }

      const analysis = await analyzeImage(options.image, requirements);
      const suggestions = getTextPlacementSuggestions(analysis, requirements);

      console.log(chalk.green('✅ Analysis complete!'));
      console.log(chalk.cyan('\n📊 Image Info:'));
      console.log(`  Size: ${analysis.image_size.join(' x ')}`);
      console.log(`  Brightness: ${analysis.color_scheme.brightness.toFixed(1)}`);
      console.log(`  Color Family: ${analysis.color_scheme.color_family}`);

      console.log(chalk.cyan('\n🎯 Placement Suggestions:'));
      suggestions.forEach((s, i) => {
        console.log(`\n  ${i + 1}. "${s.content}"`);
        console.log(`     Position: ${s.placement.position_name}`);
        console.log(`     Type: ${s.placement.type}`);
      });

      const result = { analysis, suggestions };

      if (options.output) {
        fs.writeFileSync(options.output, JSON.stringify(result, null, 2));
        console.log(chalk.green(`\n💾 Result saved to: ${options.output}`));
      }
    } catch (error) {
      console.error(chalk.red('❌ Error:'), error.message);
      process.exit(1);
    }
  });

// Command: render
program
  .command('render')
  .description('Render text on image')
  .requiredOption('-i, --image <path>', 'Path to input image')
  .requiredOption('-o, --output <path>', 'Path for output image')
  .requiredOption('-p, --placements <json>', 'Placements JSON string or file path')
  .option('-c, --choices <json>', 'User choices JSON string', '{}')
  .action(async (options) => {
    try {
      console.log(chalk.blue('🎨 Rendering text on image...'));
      console.log(chalk.gray(`Input: ${options.image}`));
      console.log(chalk.gray(`Output: ${options.output}`));

      let placements;
      let choices;

      try {
        placements = JSON.parse(options.placements);
      } catch {
        if (fs.existsSync(options.placements)) {
          placements = JSON.parse(fs.readFileSync(options.placements, 'utf8'));
        } else {
          throw new Error('Placements must be valid JSON string or file path');
        }
      }

      try {
        choices = JSON.parse(options.choices);
      } catch {
        if (fs.existsSync(options.choices)) {
          choices = JSON.parse(fs.readFileSync(options.choices, 'utf8'));
        } else {
          throw new Error('Choices must be valid JSON string or file path');
        }
      }

      const outputPath = await renderTextOnImage(
        options.image,
        options.output,
        placements,
        choices
      );

      console.log(chalk.green('✅ Text rendered successfully!'));
      console.log(chalk.green(`💾 Output saved to: ${outputPath}`));
    } catch (error) {
      console.error(chalk.red('❌ Error:'), error.message);
      process.exit(1);
    }
  });

// Command: workflow
program
  .command('workflow')
  .description('Run complete workflow: separate -> analyze -> render')
  .requiredOption('-p, --prompt <prompt>', 'User prompt')
  .requiredOption('-i, --image <path>', 'Path to base image')
  .requiredOption('-o, --output <path>', 'Path for output image')
  .option('--font-style <style>', 'Font style (modern, traditional, calligraphy, cartoon)', 'modern')
  .option('--effects <effects>', 'Comma-separated effects (shadow,outline,box)', '')
  .option('--position <position>', 'Text position (top,bottom,center,auto)', 'auto')
  .action(async (options) => {
    try {
      console.log(chalk.blue('🚀 Starting complete workflow...\n'));

      // Step 1: Separate prompt
      console.log(chalk.yellow('Step 1/3: Separating prompt...'));
      const separation = await separatePrompt(options.prompt);
      console.log(chalk.green('✅ Prompt separated'));
      console.log(chalk.cyan('Image prompt:'), separation.image_prompt);

      if (!separation.has_text) {
        console.log(chalk.yellow('⚠️ No text detected in prompt, copying image only'));
        fs.copyFileSync(options.image, options.output);
        return;
      }

      // Step 2: Analyze image
      console.log(chalk.yellow('\nStep 2/3: Analyzing image...'));
      const analysis = await analyzeImage(options.image, separation.text_requirements);
      const suggestions = getTextPlacementSuggestions(analysis, separation.text_requirements);
      console.log(chalk.green('✅ Analysis complete'));
      console.log(chalk.cyan('Safe zones found:'), analysis.safe_zones.length);

      // Step 3: Render
      console.log(chalk.yellow('\nStep 3/3: Rendering text...'));
      const userChoices = {
        font_style: options.fontStyle,
        text_position: options.position,
        effects: options.effects.split(',').filter(e => e),
        text_color: analysis.color_scheme.suggested_text_color
      };

      const outputPath = await renderTextOnImage(
        options.image,
        options.output,
        suggestions,
        userChoices
      );

      console.log(chalk.green('\n✅ Workflow completed successfully!'));
      console.log(chalk.green(`💾 Final image: ${outputPath}`));
    } catch (error) {
      console.error(chalk.red('❌ Error:'), error.message);
      process.exit(1);
    }
  });

// Command: check
program
  .command('check')
  .description('Check if Python environment is properly configured')
  .action(() => {
    console.log(chalk.blue('🔧 Checking environment...'));

    const hasPython = checkPythonEnvironment();
    if (hasPython) {
      console.log(chalk.green('✅ Python is available'));
    } else {
      console.log(chalk.red('❌ Python is not available'));
      console.log(chalk.yellow('Please install Python 3.8+ and ensure it\'s in your PATH'));
    }

    // Check Node.js version
    const nodeVersion = process.version;
    console.log(chalk.cyan('Node.js version:'), nodeVersion);

    // Check package version
    console.log(chalk.cyan('Package version:'), pkg.version);
  });

// Command: download-fonts
program
  .command('download-fonts')
  .description('Download font files for better text rendering')
  .option('--all', 'Download all fonts')
  .option('--list', 'List available fonts')
  .argument('[fonts...]', 'Specific fonts to download')
  .action(async (fonts, options) => {
    const { downloadFonts, FONTS } = require('../scripts/download-fonts');
    
    if (options.list) {
      console.log(chalk.blue('📋 Available fonts:\n'));
      for (const [name, info] of Object.entries(FONTS)) {
        console.log(`  ${chalk.cyan(name)}`);
        console.log(`      ${info.description}\n`);
      }
      console.log(chalk.gray('Usage: pto download-fonts --all'));
      console.log(chalk.gray('       pto download-fonts NotoSansCJKsc-Bold.otf'));
      return;
    }
    
    if (options.all) {
      await downloadFonts();
    } else if (fonts.length > 0) {
      await downloadFonts(fonts);
    } else {
      // Download minimal set
      await downloadFonts(['NotoSansCJKsc-Bold.otf', 'Roboto-Bold.ttf']);
    }
  });

// Parse arguments
program.parse();

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
