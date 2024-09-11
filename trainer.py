import torch
import torch.nn as nn
import torch.nn.functional as F

class distillation_DDPM_trainer(nn.Module):
  def __init__(self, T_model, S_model, T_sampler, S_sampler, distill_features = False):
    
    super().__init__()
    
    self.T_model = T_model
    self.S_model = S_model
    self.T_sampler = T_sampler
    self.S_sampler = S_sampler
    self.distill_features = distill_features
        
  def forward(self, x_t, c, t, CFG_scale=1):
        """
        Perform the forward pass for knowledge distillation.
        """
        ############################### TODO ###########################
        if self.distill_features :
            # Teacher model forward pass (in evaluation mode)
            with torch.no_grad():
                #teacher_output, teacher_features = self.T_model.forward_features(x_t, t)
                teacher_output, teacher_features = self.T_model.apply_model(x_t, t, is_feature=self.distill_features)

            # Student model forward pass
            #student_output, student_features = self.S_model.forward_features(x_t, t)
            student_output, student_features = self.S_model.apply_model(x_t, t, is_feature=self.distill_features)
    
            output_loss = F.mse_loss(student_output, teacher_output, reduction='mean')
            
            feature_loss = 0
            for student_feature, teacher_feature in zip(student_features, teacher_features):
                feature_loss += F.mse_loss(student_feature, teacher_feature, reduction='mean')
                
            total_loss = output_loss + feature_loss / len(student_features)
            
        ############################### TODO ###########################       
        
        else:
            with torch.no_grad():
                teacher_output = self.T_model.apply_model(x_t, t)

            # Student model forward pass
            student_output = self.S_model.apply_model(x_t, t)
            
            output_loss = F.mse_loss(student_output, teacher_output, reduction='mean')
            total_loss = output_loss
            
        # Teacher model forward pass (in evaluation mode)
        with torch.no_grad():
            T_output, x_prev, pred_x0 = self.T_sampler.cache_step(x_t, c, t, 
                                                                  use_original_steps = True, 
                                                                  unconditional_guidance_scale = CFG_scale) # 1 or none = no guidance, -1 = uncond

        # # Student model forward pass
        # S_output = self.S_model.apply_model(x_t, t, c)
        
        # output_loss = F.mse_loss(T_output, S_output, reduction='mean')
        # total_loss = output_loss

       
        return output_loss, total_loss, x_prev