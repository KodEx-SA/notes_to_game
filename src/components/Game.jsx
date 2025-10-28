import React, { useEffect } from 'react';
import Phaser from 'phaser';
import axios from 'axios';

const Game = ({ keywords }) => {
  useEffect(() => {
    const config = {
      type: Phaser.AUTO,
      width: 800,
      height: 600,
      parent: 'game-container',
      scene: {
        preload: preload,
        create: create,
        update: update,
      },
      physics: { default: 'arcade', arcade: { gravity: { y: 0 } } },
      backgroundColor: '#1a1a1a',
    };

    let player, coins, score = 0, scoreText;

    function preload() {
      // Placeholder assets (replace with actual sprites)
      this.load.image('player', 'https://example.com/player.png');
      this.load.image('coin', 'https://example.com/coin.png');
    }

    function create() {
      player = this.physics.add.sprite(100, 450, 'player').setScale(0.5);
      player.setCollideWorldBounds(true);

      coins = this.physics.add.group();
      keywords.forEach((keyword, index) => {
        const x = 800 + index * 200;
        const coin = coins.create(x, 300, 'coin').setScale(0.3);
        coin.setData('keyword', keyword);
        coin.setVelocityX(-200);
        this.add.text(x, 300 - 20, keyword, {
          fontSize: '16px',
          fill: '#00ff88',
        }).setOrigin(0.5);
      });

      scoreText = this.add.text(16, 16, 'Score: 0', {
        fontSize: '24px',
        fill: '#00ff88',
      });

      this.physics.add.overlap(player, coins, collectCoin, null, this);

      this.input.keyboard.on('keydown-SPACE', () => {
        player.setVelocityY(-300);
      });
    }

    function collectCoin(player, coin) {
      coin.destroy();
      score += 10;
      scoreText.setText(`Score: ${score}`);
      axios.post(`${import.meta.env.VITE_API_URL}/scores`, {
        user_id: 'anonymous',
        score,
      }).catch((error) => console.error('Score save error:', error));
    }

    function update() {
      const cursors = this.input.keyboard.createCursorKeys();
      if (cursors.left.isDown) {
        player.setVelocityX(-160);
      } else if (cursors.right.isDown) {
        player.setVelocityX(160);
      } else {
        player.setVelocityX(0);
      }
    }

    const game = new Phaser.Game(config);
    return () => game.destroy(true);
  }, [keywords]);

  return <div id="game-container"></div>;
};

export default Game;