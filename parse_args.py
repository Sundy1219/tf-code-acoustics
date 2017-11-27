
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
import os
import pickle
import time
import logging
import util.parse_opt as parse_opt
import argparse




def parse_args(args_list): 
    """ 
     #Parses the command line input.
    """ 
    parser = parse_opt.MyArgumentParser(description='this train tool',fromfile_prefix_chars='@')
    
    parser.add_argument('--num-threads', dest='num_threads', type=int, default=1,
            help='number threads (int, default = 1)')
        
    parser.add_argument('--tf-save-path', dest='tf_save_path', 
            type=str, default=None, 
            help='TensorFlow save path name for the run (allow multiples run with the same output path)'
            '(str, default = None)')

    parser.add_argument('--max-epoch', dest='max_epoch', type=int, default=None, 
            help='Max epoch to train (no limitation if not provided)' '(int, default = None)') 
 
    parser.add_argument('--Debug', dest='Debug', type=bool, default=False,
            help='debug or not'
            '(bool, default = False)')
    
    parser.add_argument('--use-config-file-if-checkpoint-exists', dest='use_config_file_if_checkpoint_exists',type=bool,
            default=False,
            help='use config file train model'
            '(bool, default = False)')

    parser.add_argument('--checkpoint-dir', dest='checkpoint_dir', type=str,
            default='outdir',
            help='save dir' '(str, default = outdir)')

    parser.add_argument('--queue-cache', dest='queue_cache', type=int,
            default=100,
            help='input data cache' '(int, default = 100)')

    parser.add_argument('--max-input-seq-length', dest='max_input_seq_length',type=int,
            default=1500,
            help='allow input max input length' '(int, default = 1500)')

    parser.add_argument('--max-target-seq-length', dest='max_target_seq_length',type=int,
            default=1500,
            help='allow target max input length' '(int, default = 1500)')
    
    parser.add_argument('--scp-file', dest='scp_file', type=str,
            default=None,
            help='train scp file' '(str, default = None)')

    parser.add_argument('--label', dest='label', type=str,
            default=None,
            help='train label file' '(str, default= None)')

    parser.add_argument('--restore-training', dest='restore_training', type=bool,
            default=False,
            help='restore training' '(bool, default = False)')

    parser.add_argument('--log-file', dest='log_file', type=str,
            default='log',
            help='log file' '(str, default = log)')

    parser.add_argument('--log-level', dest='log_level', type=str,
            default='INFO',
            help='log level' '(str, default = INFO)')

    '''
        ##add feature option
    '''
    feature_opt = parser.add_argument_group(title='feature_opt', 
            description='feature option relation parameters')

    feature_opt.add_argument('--right-context', '--rcxt', dest='rcxt',
            type=int, default=0,
            help='right context frame number'
            ' (int, default = 0)')
    
    feature_opt.add_argument('--left-context', '--lcxt', dest='lcxt',
            type=int, default=0,
            help='left context frame number'
            ' (int, default = 0)')

    feature_opt.add_argument('--skip-frames', dest='skip_frame',
            type=int, default=1,
            help='skip frame number'
            ' (int, default = 1)')
    
    feature_opt.add_argument('--start-frames', dest='start_frames',
            type=int, default=0,
            help='start frame ,it must be lt skip-frames'
            ' (int, default = 0)')


    '''
       #add train common option
    '''
    train_common_opt = parser.add_argument_group(title='train_common_opt', 
            description='training common option relation parameters')

    train_common_opt.add_argument('--steps-per-checkpoint', dest='steps_per_checkpoint',
            type=int, default=1000,
            help='save frequency'
            '(int, default = 1000)')

    train_common_opt.add_argument('--learning-rate', dest='learning_rate',
            type=float, default=1.0, 
            help='learning rate for NN training'
            ' (float, default = 1.0)')

    train_common_opt.add_argument('--batch-size', dest='batch_size', type=int, 
            default=1,
            help='Number of streams in the Multi-stream training'
            '(int, default = 1)')
    
#    train_common_opt.add_argument('--num-streams', dest='nstreams', type=int,
#            default=1,
#            help='Number of streams in the Multi-stream training'
#            '(int, default = 1)')

    train_common_opt.add_argument('--num-frames-batch', 
            dest='num_frames_batch', 
            type=int, default=20,
            help='Length of \'one stream\' in the Multi-stream training'
            '(int, default = 20)')

    train_common_opt.add_argument('--init-scale', dest='init_scale', type=float,
            default=0.01,
            help='bound of the range of random values to generate'
            '(float, default = 0.01)')

    train_common_opt.add_argument('--lr-decay-factor', dest='lr_decay_factor', type=float,
            default = 0.5,
            help='learn rate decay factor'
            '(float, default = 0.5)')

    train_common_opt.add_argument('--grad-clip', dest='grad_clip', type=float,
            default = 5.0,
            help='Clipping the accumulated gradients (per-updates)'
            '(float, default = 5.0)')



    train_common_opt.set_defaults(cross_validate=False)
    train_common_opt.add_argument('--cross-validate', dest='cross_validate',
            action='store_true',
            help='Perform cross-validation (don\'t back-propagate)'
            ' (bool, default = false)')

    train_common_opt.add_argument('--momentum', type=float, default=0.0,
            help='Momentum' 
            ' (float, default = 0.0)')

    train_common_opt.add_argument('--objective-function', dest='objective_function',
            type=str, default='ctc',
            help='Objective function : ctc|xent|mse'
            '(string, default = "ctc")')
    
    train_common_opt.add_argument('--report-step', dest='report_step', type=int,
            default=100,
            help='Step (number of sequences) for status reporting'
            ' (int, default = 100)')

    train_common_opt.add_argument('--time-major', dest='time_major', type=bool,
            default=True,
            help='time major'
            '(bool, default = True)')

    train_common_opt.add_argument('--output-size', dest='output_size',type=int,
            default=None,
            help='output dim' '(int, default = None)')

    train_common_opt.add_argument('--forward-only', dest='forward_only', type=bool,
            default=False,
            help='only calculate forward'
            '(bool, default = False)')



    '''
       #add lstm train relation option
    '''
    train_lstm_opt = parser.add_argument_group(title='train_lstm_opt', 
            description='training lstm option relation parameters')

    train_lstm_opt.add_argument('--frame-num-limit',dest='frame_num_limit',
            type=int, default=1500,
            help='Sentence max number of frames' 
            ' (double, default = 1500)')
    train_lstm_opt.add_argument('--num-layers', dest='num_layers', type=int,
            default = 3,
            help='Nnet number layers'
            '(int, default = 3)')

    train_lstm_opt.add_argument('--hidden-size', dest='hidden_size', type=int,
            default=1024,
            help='Number of cells for one direction in LSTM '
            '(int, default = 1024)')

    train_lstm_opt.add_argument('--proj-dim', dest='proj_dim', type=int, 
            default=512,
            help='Number of LSTM recurrent units (int, default = 512)');

    train_lstm_opt.add_argument('--dropout-input-keep-prob', dest='dropout_input_keep_prob', type=float,
            default=1.0,
            help='dropout input keep prob'
            '(float, default = 1.0)')

    train_lstm_opt.add_argument('--dropout-output-keep-prob', dest='dropout_output_keep_prob', type=float,
            default=1.0,
            help='dropout output keep prob'
            '(float, default = 1.0)')

    train_lstm_opt.add_argument('--rnn-state-reset-ratio', dest='rnn_state_reset_ratio', type=float,
            default=0.0,
            help='rnn state reset ratio'
            '(bool, default = 0.0)')

    '''
       #add mutually exclusive group 4 choise 1
    '''
#    group = parser.add_mutually_exclusive_group(required=True) 
#    group.set_defaults(train=False) 
#    group.set_defaults(file=None) 
#    group.set_defaults(record=False) 
#    group.set_defaults(evaluate=False) 
#    group.add_argument('--train', dest='train', action='store_true', help='Train the network') 
#    group.add_argument('--file', type=str, help='Path to a wav file to process') 
#    group.add_argument('--record', dest='record', action='store_true', help='Record and write result on the fly') 
#    group.add_argument('--evaluate', dest='evaluate', action='store_true', help='Evaluate WER against the test_set') 

    '''
        #dict choise
    '''
    args = parser.parse_args(args_list) 
    if args.start_frames >= args.skip_frame and args.start_frames != 0:
        raise 'error feature option'

    if args.output_size <= 0:
        raise 'output_size isn\'t less equal 0'

    if args.scp_file is None:
        raise 'input scp file it\'s None'

    if args.label is None:
        raise 'input label it\'s None'
    
    return args.__dict__


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    print(args)
    for k,v in args.iteritems():
        print(k+':\t'+str(v))


